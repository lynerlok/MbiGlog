#! /usr/bin/env Rscript
#R script to get gene axpression after NGS pipeline
#Based on the article of :
#Contreras-Lopez O, Moyano TC, Soto DC, Gutiérrez RA (2018).
#Step-by-Step Construction of Gene Co-expression Networks from High-Throughput Arabidopsis RNA Sequencing Data.
#Methods Mol Biol 1761, 275-301.

args = commandArgs(trailingOnly = TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)==0) {
  stop("At least one argument must be supplied", call.=FALSE)
}

dir_sam = args[1]
dir_gtf = args[2]
dir_analysis_output = args[3]
dir_protein_coding = args[4]

# source("http://bioconductor.org/biocLite.R")
# biocLite("Rsubread")
library(Rsubread)

#Then, it is necessary to run the feature counts for all SAM files. First, select the SAM files:
sam.list <- dir(path=dir_sam, pattern=".sam")
sam.list.path = file.path(dir_sam,sam.list)

#Since there are different types of library preparation and run configurations, the user should use the appropriate one. In this example, we use the non-stranded (strandSpecific=0) option. For strand-specific library preparations, the user may refer to provided supplementary files.
#The following command runs the program using 2 threads and store the output in "fc0" object.

fc0 <- featureCounts( sam.list.path, annot.ext= dir_gtf ,isGTFAnnotationFile=T, allowMultiOverlap=T, isPairedEnd=F, nthreads=2, strandSpecific=0)

#Then, we save the counts and associated stats in tab delimited files:
write.table(fc0$counts, file.path(dir_analysis_output,"fc0.counts.txt"), sep="\t", col.names=NA, quote=F)
write.table(fc0$stat, file.path(dir_analysis_output,"fc0.stat.txt"), sep="\t", row.names=F, quote=F)

# Finally, we select protein coding genes with reads counts:
protein_coding<-as.matrix(read.table(dir_protein_coding))
counts<-fc0$counts[protein_coding,]
counts <- counts[rowSums(counts)>0,]

#Normalization of gene reads counts from RNA-seq data.


#The following commands can perform the mentioned normalization.
# source("http://bioconductor.org/biocLite.R")
# biocLite("EBSeq")
library(EBSeq)
NormData <- GetNormalizedMat(counts, MedianNorm(counts))

#The resulting gene expression matrix contains unique row identifiers and row counts obtained from different experiments on each column. After normalization, it is recommended to delete very low counts data or sum a unit to all data in order to avoid values equal to zero. Then is useful to generate a logarithmic matrix of the data to standardize the variance.
NormData.log <- log2(NormData+1)

write.table(NormData.log, file.path(dir_analysis_output,"testCytoscape1.tab"), sep="\t", col.names=T, row.names = T, quote=F)

def parser(pathway_file):
    list_seq = []
    with open(pathway_file, 'r') as file:
        txt = file.read()
        raw_fasta_list = txt.split(">")
        raw_fasta_list.remove("")
        for seq in raw_fasta_list:
            seq_dict = {}
            id = seq.split()[0]
            name = seq.split("\n")[0].split(" ")[1:]
            name = " ".join(name)
            seq = seq.split("\n")[1:]
            seq = "".join(seq)
            seq_dict['id'] = id
            seq_dict['name'] = name
            seq_dict['sequence'] = seq
            list_seq.append(seq_dict)
    return list_seq


if __name__ == "__main__":
    import os
    #dict = parser("./arabi.fasta")
    #print( "id : " , dict['id_gene'])
    #print("nom : " , dict['nom_gene'])
    #print("sequence : \n",dict['sequence'])

    
    



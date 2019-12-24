/*
PARSER XML
04/11/2019
ANDRÉ Charlotte
GALLARDO Jean Clément
LECOMTE Maxime
LAPORTE Antoine
MERCHADOU Kévin

*/

const struct = (groups) => {
	let gene_ID = {
		"GLYCOLYSIS": [],
		"proteine" : []
	};
	groups.forEach(cur =>
		(cur.attributes[0].name === 'ID') ?
		gene_ID.GLYCOLYSIS.push(cur.attributes[2].nodeValue) :
		(cur.attributes.length === 3) ?
		gene_ID.proteine.push(cur.attributes[2].nodeValue) : '');
	return gene_ID;
}

const parseXML = (text) => {
	let parser = new DOMParser();
	let doc = parser.parseFromString(text, "application/xml");
	let secStruct = struct(doc.querySelectorAll("Gene,Protein")); // balise a recuperer
}


const getContent = (ev) => {
    //  console.log(ev);
     let f = ev.target.files[0];
     let reader = new FileReader();
     reader.onload = (e) => {
         let text = reader.result;
         parseXML(text);
     }
    reader.readAsText(f);
 };

//Add Event Listener
let whatifBrowse = document.querySelector('#xml');
whatifBrowse.addEventListener('change', getContent);

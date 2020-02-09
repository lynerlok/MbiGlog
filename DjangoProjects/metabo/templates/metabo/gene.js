/*
ANDRÉ Charlotte
GALLARDO Jean Clément
LECOMTE Maxime
LAPORTE Antoine
MERCHADOU Kévin
GALLARDO Jean-Clément
*/

const struct = (groups) => {
	// console.log(groups);
	let gene_ID = {
		"gene_ID" : [], // contiendra la liste gene pour un pwyID donné

	};

	groups.forEach(cur =>
		(cur.attributes[0].name === 'ID') ?
		gene_ID.gene_ID.push(cur.attributes[2].nodeValue) : 0);
	return gene_ID;
	}

const parseXML = (text) => {
	let parser = new DOMParser();
	let doc = parser.parseFromString(text, "application/xml");
	let secStruct = struct(doc.querySelectorAll("Gene"));
	console.log(secStruct);
}


const getContent = (ev) => {
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

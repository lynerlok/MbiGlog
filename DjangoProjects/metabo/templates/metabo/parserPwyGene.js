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
	console.log(groups);
	let pwy_ID = {
		"GeneID": [],
		"ReactionList" : []
	};
	groups.forEach(cur =>
		(cur.attributes[0].name === 'ID') ?
		pwy_ID.GeneID.push(cur.attributes[2].nodeValue) :
		pwy_ID.ReactionList.push(cur.attributes[2].nodeValue)); // recupere aussi les pathway ressource
	return pwy_ID;
}

const parseXML = (text) => {
	let parser = new DOMParser();
	let doc = parser.parseFromString(text, "application/xml");
	let secStruct = struct(doc.querySelectorAll("Pathway,Reaction")); // balise a recuperer
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

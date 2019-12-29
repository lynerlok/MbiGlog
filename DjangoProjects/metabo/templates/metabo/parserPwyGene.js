//
// PARSER XML
// 04/11/2019
// ANDRÉ Charlotte
// GALLARDO Jean Clément
// LECOMTE Maxime
// LAPORTE Antoine
// MERCHADOU Kévin



const struct = (groups) => {
	console.log(groups);
	let orgid = [];
	let gene_Id = [];
	let pwy_ID = {
		"orgid" : [],
		"pwyID" : [],// contiendra la liste pwy pour un gene ID donné
		"pwyList" : [],
		"ReactionList" : [] // contiendra la liste des reaction pour un pwy en cle
	};

	groups.forEach(cur =>
		(cur.textContent.match(/[A-Z]*:[A-Z]*[0-9]*/g)) ? pwy_ID.orgid.push(cur.textContent.match(/[A-Z]*:[A-Z]*[0-9]*[A-Z]*[0-9]*/g)) :
		(cur.attributes[0].name === 'ID') ?
		pwy_ID.pwyID.push(cur.attributes[2].nodeValue) :
		(cur.attributes.length === 4) ?
		pwy_ID.pwyList.push(cur.attributes[2].nodeValue) :
		pwy_ID.ReactionList.push(cur.attributes[2].nodeValue)); // attention il a rajoute des pathway ressources comment XYLCAT-PWY
	return pwy_ID;
}

const parseXML = (text) => {
	let parser = new DOMParser();
	let doc = parser.parseFromString(text, "application/xml");
	let secStruct = struct(doc.querySelectorAll("Pathway,query,Reaction") );// balise a recuperer
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

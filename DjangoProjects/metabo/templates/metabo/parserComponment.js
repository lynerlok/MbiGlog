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
	// console.log(groups);
	let componment = {
		"proteinID": []
	};
	groups.forEach(cur =>
		(cur.attributes[1].nodeValue.match(/C:[a-z]*/g)) ?
		componment.proteinID.push(cur.attributes[1].nodeValue):0);// recupere aussi les pathway ressource
	return componment;
}

const parseXML = (text) => {
	let parser = new DOMParser();
	let doc = parser.parseFromString(text, "application/xml");
	let secStruct = struct(doc.querySelectorAll("property")); // balise a recuperer
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

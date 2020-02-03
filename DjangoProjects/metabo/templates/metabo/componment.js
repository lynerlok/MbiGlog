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
	let componment = {
		"location": [], // lieu ou les reactions se font
		"pwys" : []

	};
	groups.forEach(cur =>
		(cur.attributes[1].nodeValue.match(/C:[a-z]*/g)) ?
		componment.location.push(cur.attributes[1].nodeValue) :
		cur.attributes[0].value.match(/Pathway/g) ?
		componment.pwys.push(cur.attributes[1].name+"= "+cur.attributes[1].value) : 0);
	return componment;
}

const parseXML = (text) => {
	let parser = new DOMParser();
	let doc = parser.parseFromString(text, "application/xml");
	let secStruct = struct(doc.querySelectorAll("dbReference,property")); // balise a recuperer
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

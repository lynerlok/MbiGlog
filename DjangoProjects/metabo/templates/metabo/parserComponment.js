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
		"orgid" : [], // contiendra l'ID du gene
		"location": [], // lieu ou les reactions se font
		"enzName" : [] // nom de l'enzyme
	}; // /[[A-Z]* *[A-Z]*/g
	groups.forEach(cur =>
		(componment.enzName.length === 0 && cur.attributes[0].value.match("entry name") && cur.attributes[1].value.match(/[[A-Z][a-z]*_[A-Z][a-z]*/g)) ?
		componment.enzName.push(cur.attributes[1].value) :
		(cur.attributes[1].nodeValue.match(/C:[a-z]*/g)) ?
		componment.location.push(cur.attributes[1].nodeValue) : componment.orgid.length === 0 && cur.attributes[0].value.match("gene ID") && cur.attributes[1].value.match(/[A-Z]*[0-9]*/g) ? componment.orgid.push(cur.attributes[1].value) : 0);
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

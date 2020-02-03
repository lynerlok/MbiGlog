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
	let pwy_ID = {
		"enzName" : [],
		"cofactor": []
	};

	groups.forEach(cur =>
		cur.attributes.length === 0 ?
		pwy_ID.cofactor.push(cur.textContent) :
		(pwy_ID.enzName.length === 0 && cur.attributes[0].value.match("entry name") && cur.attributes[1].value.match(/[A-Z][a-z]*_[A-Z][a-z]*/g)) ?
		pwy_ID.enzName.push(cur.attributes[1].value) : 		pwy_ID.cofactor.length != 0 ?
		delete pwy_ID.cofactor[0] : 0);
	return pwy_ID;
}

const parseXML = (text) => {
	let parser = new DOMParser();
	let doc = parser.parseFromString(text, "application/xml");
	let secStruct = struct(doc.querySelectorAll("name,property") );// balise a recuperer
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

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

	let metabolism = {
		"name" : []
	};

	groups.forEach(cur =>
 	metabolism.name.push(cur.textContent));
	return metabolism;
}

const parseXML = (text) => {
	let parser = new DOMParser();
	let doc = parser.parseFromString(text, "application/xml");
	let secStruct = struct(doc.querySelectorAll("common-name") );// balise a recuperer
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

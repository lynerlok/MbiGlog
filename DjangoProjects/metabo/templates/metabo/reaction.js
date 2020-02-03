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
		"ReactionList" : [], // contiendra le nom de chaque reaction
		"metabolites" : []
	};

	groups.forEach(cur =>
		(cur.attributes.length != 4) ?
		pwy_ID.ReactionList.push(cur.attributes[2].nodeValue) : 0); // attention il a rajoute des pathway ressources comment XYLCAT-PWY
	return pwy_ID;
}

const parseXML = (text) => {
	let parser = new DOMParser();
	let doc = parser.parseFromString(text, "application/xml");
	let secStruct = struct(doc.querySelectorAll("Reaction") );// balise a recuperer /////// Pathway,query,
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

/*
PARSER XML
04/11/2019
ANDRÉ Charlotte
GALLARDO Jean Clément
LECOMTE Maxime
LAPORTE Antoine
MERCHADOU Kévin

*/

// const struct = (groups) => {
	// console.log(groups);
	let path = {
		"gene_List" : [], // contiendra la liste gene pour un pwyID donné
		"pwyID" : [],  // contiend le pwyID
        "pwyList" : [], // nom de chaque pwyid
		"proteine" : [] // contiendra la liste des enzymes pour un chaque gene
	};
//
// 	groups.forEach(cur =>
// 		(cur.textContent.match(/[A-Z]*:[A-Z]*[0-9]*/g)) ? gene_ID.pwyID.push(cur.textContent.match(/[A-Z]*:[A-Z]*-[0-9]*/g)) :
// 		(cur.attributes[0].name === 'ID') ?
// 		path.gene_ID.push(cur.attributes[2].nodeValue) :
// 		(cur.attributes.length === 3) ?
// 		path.proteine.push(cur.attributes[2].nodeValue) : 0);
// 	return path;
// 	}
//
// const parseXML = (text) => {
// 	let parser = new DOMParser();
// 	let doc = parser.parseFromString(text, "application/xml");
// 	let secStruct = struct(doc.querySelectorAll("query,Gene,Protein")); // balise a recuperer
// 	console.log(secStruct);
// }
//
//
// const getContent = (ev) => {
//      let f = ev.target.files[0];
//      let reader = new FileReader();
//      reader.onload = (e) => {
//          let text = reader.result;
//          parseXML(text);
//      }
//     reader.readAsText(f);
//  };
//
// //Add Event Listener
// let whatifBrowse = document.querySelector('#xml');
// whatifBrowse.addEventListener('change', getContent);

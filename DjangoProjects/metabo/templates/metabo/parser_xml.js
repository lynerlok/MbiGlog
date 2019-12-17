/*
PARSER XML
04/11/2019
Lecomte MAXIME
Merchadou KEVIN


autres :
Laporte ANTOINE
*/

const struct = (groups) => {
	// console.log(groups);
	let gene_ID = {
		"GLYCOLYSIS": []
	};

	groups.reduce((accu, cur) => {
		if (cur.attributes[0].name === 'ID') {
			gene_ID.GLYCOLYSIS.push(cur.attributes[2].nodeValue); // recuperation frameid
			return accu;
		}
	}, []);
	return gene_ID;
}

const parseXML = (text) => {
	let parser = new DOMParser();
	let doc = parser.parseFromString(text, "application/xml");
	let secStruct = struct(querySelectorAll('Gene', doc)); // balise a recuperer

	console.log('secstruc',secStruct);
}


const getContent = (ev) => {
    //  console.log(ev);
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

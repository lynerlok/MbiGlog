var list_node = [];



function loadFile() {
    var input, file, fr;

    if (typeof window.FileReader !== 'function') {
        alert("The file API isn't supported on this browser yet.");
        return;
    }

    input = document.getElementById('fileinput');
    if (!input) {
        alert("Um, couldn't find the fileinput element.");
    } else if (!input.files) {
        alert("This browser doesn't seem to support the `files` property of file inputs.");
    } else if (!input.files[0]) {
        alert("Please select a file before clicking 'Load'");
    } else {
        file = input.files[0];
        fr = new FileReader();
        fr.onload = receivedText;
        fr.readAsText(file);
    }

    function receivedText(e) {
        let lines = e.target.result;
        var obj = JSON.parse(lines);
        console.log(obj);

        cy = cytoscape(
            {
                container: document.getElementById('cy-visu'),
                elements: obj,
                style: [ // the stylesheet for the graph
                    {
                        selector: 'node',
                        style: {
                            'background-color': '#666',
                            'label': 'data(id)'
                        }
                    },

                    {
                        selector: 'edge',
                        style: {
                            'width': 3,
                            'line-color': '#aabdaa',
                            'target-arrow-color': '#ccc',
                            'target-arrow-shape': 'triangle',
                            'color': '#107d10'
                        }
                    }
                ],

                layout:
                    {
                        name: 'grid'
                    }
            });

        cy.layout({
            name: 'circle'
        }).run();
    };
}

function saveFile() {
    var data = cy.json(true);
    var data_to_save = [];
    for (i = 0; i < data.elements.length; i++) {
        data_to_save.push({
            "data" : data.elements[i].data
            ,
            "position" : data.elements[i].position
        })
    }
    download(JSON.stringify(data_to_save), "test.json","data:text/json;charset=utf8")
}

// Function to download data to a file
function download(data, filename, type) {
    var file = new Blob([data], {type: type});
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a"), url = URL.createObjectURL(file);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 0);
    }
}

// Create gene visualization with .tab file
function readFile(path_data) {
    cy.elements().remove();
    fetch(path_data)
        .then(response => {
            if (response.ok) {
                console.log("ok");
                return response.text();
            } else {
                console.log("Invalid path");
            }
        })
        .then(txt => parseFile(txt))
        .catch(err => console.log(err));
}

const parseFile = (text) => {
    var lines = text.split("\n");
    lines.reduce(parseLine, []);
    layout_graph("cose");
};

const parseLine = (accu, line, i) => {
    var key = line.substring(0, 4).trim();
    if (key === 'Var1') {
        console.log("it's a header");
    } else if (key !== 'Var1') {
        cutGENE(accu, line);
    }
};

const cutGENE = (accu, line) => {
    var cuts = [
        {
            start: 0,
            end: 9,
            field: 'src_gene',
            type: 'string'
        },
        {
            start: 11,
            end: 19,
            field: 'trg_gene',
            type: 'string'
        },
        {
            start: 21,
            end: 36,
            field: 'corr_type',
            type: 'string'
        }
    ];
    var obj = cuts.reduce((acc, cut) => {
            acc[cut.field] = line.substring(cut.start - 1, cut.end);
            return acc;
        },
        {});
    create_gene_visu(obj, line);
};

function check_id(id_node) {
    var check = true;
    if (cy.getElementById(id_node).selectable()) {
        check = false;
    }
    return check;
}

function create_gene_visu(obj, line) {
    var id_src = obj.src_gene;
    var id_trg = obj.trg_gene;
    var check_src = check_id(id_src);
    var check_trg = check_id(id_trg);

    if (check_src === true && id_src !== "") {
        var src_node = cy.add({
            group: 'nodes',
            data: {id: obj.src_gene, name: obj.src_gene},
            style: {label: obj.src_gene, 'text-valign': 'center'}
        });
        node_style('red', 'rectangle', src_node);
        create_list(src_node.id());
        list_node.push(src_node.id());
    }
    if (check_trg === true && id_trg !== "") {
        var trg_node = cy.add({
            group: 'nodes',
            data: {id: obj.trg_gene, name: obj.trg_gene},
            style: {label: obj.trg_gene, 'text-valign': 'center'}
        });
        node_style('red', 'rectangle', trg_node);
        create_list(trg_node.id());
        list_node.push(trg_node.id());
    }




    if (id_src !== "" && id_trg !== "") {
        edge = cy.add({
            group: 'edges',
            data: {
                id: line,
                source: obj.src_gene,
                target: obj.trg_gene
            },
        });
    }

}

// Modif edge style
function edge_style(color, edge) {
    edge.style('line-color', color);
    edge.style('curve-style', 'bezier');
    edge.style('target-arrow-shape', 'triangle');
    edge.style('arrow-scale', 2);
    edge.style('target-arrow-color', color);
    edge.style('text-background-color', color);
}

// Modif node style
function node_style(color, shape, node) {
    node.style('background-color', color);
    node.style('shape', shape);
    node.style('width', 'label');
}

// Add layout on graph
function layout_graph(name) {
    var layout = cy.elements().layout({
        name: name
    });
    layout.run();
}

function create_list(gene){
    var select = document.getElementById("gene-select");
    var opt = document.createElement('option');
    opt.appendChild(document.createTextNode(gene));
    opt.value = gene;
    select.appendChild(opt);
}

function neighborNode(node_selected, colorNode, colorNeig){
    var node = cy.getElementById(node_selected);
    for (var i = 0; i < node.neighborhood().length; i++){
        var edge_nei = cy.getElementById(node.neighborhood()[i].id());
        var id_nei = edge_nei.targets().id();
        var node_nei = cy.getElementById(id_nei);
        node_style(colorNeig,"rectangle",node_nei);
    }
    node_style(colorNode,"rectangle",node);
}

function clear_coloration(list_node){
    for (var i = 0; i < list_node.length; i++){
        neighborNode(list_node[i], "red", "red")
        // var node = cy.getElementById(list_node[i]);
        // node_style("red","rectangle",node);
    }
}
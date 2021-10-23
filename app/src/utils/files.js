
export const csvJSON = (csv) => {

    var lines = csv.split("\n");

    var result = [];

    var headers = lines[0].split(",").map((e) => strip_text(e));

    for (var i = 1; i < lines.length; i++) {

        var obj = {};
        var currentline = lines[i].split(",").map((e) => strip_text(e));

        for (var j = 0; j < headers.length; j++) {
            obj[headers[j]] = currentline[j];
        }

        result.push(obj);

    }
    return result;
}

export const intcsv2JSONarr = async (csv, onUploadProgress) => {

    var lines = csv.split("\n");
    // console.log("Found " + lines.length + " records.")

    var headers = lines[0].split(",").map((e) => strip_text(e));
    var column_data = {};
    headers.forEach(element => {
        column_data[element] = [];
    });
    for (var i = 1; i < lines.length; i++) {

        var currentline = lines[i].split(",").map((e) => parseInt(strip_text(e)));

        for (var j = 0; j < headers.length; j++) {
            column_data[headers[j]].push(currentline[j]);
        }
        if (i % (Math.round(lines.length / 100)) == 0) {
            // console.log((i +1)/ lines.length * 100);
            // onUploadProgress((i +1)/ lines.length * 100);
        }
    }
    return column_data;
}

export const csv2JSONarr = async (csv, onUploadProgress) => {

    var lines = csv.split("\n");
    // console.log("Found " + lines.length + " records.")

    var headers = lines[0].split(",").map((e) => strip_text(e));
    var column_data = {};
    headers.forEach(element => {
        column_data[element] = [];
    });
    for (var i = 1; i < lines.length; i++) {

        var currentline = lines[i].split(",").map((e) => strip_text(e));
        if (currentline.length!=headers.length)
            continue;
        for (var j = 0; j < headers.length; j++) {
            column_data[headers[j]].push(currentline[j]);
        }
        if (i % (Math.round(lines.length / 100)) == 0) {
            // console.log((i +1)/ lines.length * 100);
            // onUploadProgress((i +1)/ lines.length * 100);
        }
    }
    return column_data;
}

export const strip_text = (str) => {
    return str.trim().replace(/[\n\r\t]/g, '')
}
export const hist = (arr, numOfBuckets, interval) => {
    var bins = [];
    var binCount = 0;

    //Setup Bins
    for (var i = 0; i < numOfBuckets*interval; i += interval) {
        bins.push({
            binNum: binCount,
            minNum: i,
            maxNum: i + interval,
            name: i+'-'+(i+interval),
            count: 0
        })
        binCount++;
    }

    //Loop through data and add to bin's count
    for (var i = 0; i < arr.length; i++) {
        var item = arr[i];
        for (var j = 0; j < bins.length; j++) {
            var bin = bins[j];
            if (item > bin.minNum && item <= bin.maxNum) {
                bin.count++;
                break;  // An item can only be in one bin.
            }
        }
    }
    return bins;
}

export const padZeros = (str, size) => {
    while (str.length < size){
        str = '0' + str;
    }
    return str;
}
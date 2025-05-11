// #1
const arr1 = [1, 2, 3, 4, 5, 5, 2];
const arr2 = [4, 5, 6, 7, 8, 6];

const unionArray = [...new Set([...arr1, ...arr2])];
console.log('Task 1: ', unionArray);

//#2
function printEvenPositive(arr) {
    for (let i = 0; i < arr.length; i++) {
        const n = arr[i];
        if (n > 0 && n % 2 === 0) {
            console.log(n);
        }
    }
}
console.log('Task 2: ');
printEvenPositive([1, 2, 3, 4, 5, 6, -2, 0]);

//#3
function checkZero(arr) {
    if (arr.includes(0)) {
        console.log('There is no zeros');
    }
}
checkZero([1, 2, 3, 0, 5]);
checkZero([4, 7, 9]);

//#4
function printIndexOfFive(arr) {
    const idx = arr.indexOf(5);
    if (idx !== -1) {
        console.log(`Index of the element with value of 5 is: ${idx}`);
    } else {
        console.log('There is no 5');
    }
}

printIndexOfFive([2, 5, 7, 5]);
printIndexOfFive([1, 2, 3]);

//#5
function productOfElements(arr) {
    let product = 1;
    for (let i = 0; i < arr.length; i++) {
        product *= arr[i];
    }
    console.log(`${product}`);
}

productOfElements([2, 3, 4]);
productOfElements([1, 0, 5]);

//#6
function sortArray(arr) {
    if (arr.length === 0) return [];

    if (typeof arr[0] === 'string') {
        return arr.slice().sort();
    }
    if (typeof arr[0] === 'number') {
        return arr
            .slice()
            .sort((a, b) => Math.abs(a) - Math.abs(b));
    }

    return arr.slice();
}

console.log( sortArray(['банан', 'Яблуко', 'вишня']) );
console.log( sortArray([3, -1, 2, -4, 0]) );
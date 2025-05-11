const processPointsExp = function(x1, y1, x2, y2) {
    const getLocation = (x, y) => {
        if (x === 0 && y === 0)      return 'в початку координат';
        if (x === 0)                 return 'на осі Y';
        if (y === 0)                 return 'на осі X';
        if (x > 0 && y > 0)          return 'в I чверті';
        if (x < 0 && y > 0)          return 'в II чверті';
        if (x < 0 && y < 0)          return 'в III чверті';
        return 'в IV чверті';
    };

    const loc1 = getLocation(x1, y1);
    const loc2 = getLocation(x2, y2);
    const sameQ = loc1 === loc2 &&
        ['в I чверті','в II чверті','в III чверті','в IV чверті']
            .includes(loc1);

    if (sameQ) {
        const dist = Math.hypot(x2 - x1, y2 - y1);
        console.log(`Відстань між точками: ${dist}`);
    } else {
        console.log(`Точка 1 знаходиться ${loc1}, Точка 2 знаходиться ${loc2}`);
    }
};

processPointsExp(2, 3, 5, 7);
processPointsExp(-1, 4, 2, -5);
processPointsExp(0, 0, 1, -1);
processPointsExp(5, 0, -2, 3);

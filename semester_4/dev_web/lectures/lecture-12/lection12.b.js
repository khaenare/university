const costArrow = (hryv, kop) => {
    const extraHr = Math.floor(kop / 100);
    const kops = kop % 100;
    const totalHr = hryv + extraHr;

    const getForm = (n, [one, few, many]) => {
        const d10 = n % 10, d100 = n % 100;
        if (d10 === 1 && d100 !== 11) return one;
        if (d10 >= 2 && d10 <= 4 && !(d100 >= 12 && d100 <= 14)) return few;
        return many;
    };

    const hrForm  = getForm(totalHr, ['гривня', 'гривні', 'гривень']);
    const kopForm = getForm(kops,  ['копійка', 'копійки', 'копійок']);

    console.log(`${totalHr} ${hrForm} ${kops} ${kopForm}`);
};

// Тест:
costArrow(2, 75);
costArrow(0, 1);
costArrow(25, 3);
costArrow(20, 102);

export const generateString = (length: number = 15): string => {
    const allCapsAlpha = [..."ABCDEFGHIJKLMNOPQRSTUVWXYZ"];
    const allLowerAlpha = [..."abcdefghijklmnopqrstuvwxyz"];
    const allNumbers = [..."0123456789"];

    const base = [...allCapsAlpha, ...allNumbers, ...allLowerAlpha];

    const generator = (base: string[], len: number) => {
        return [...Array(len)]
            .map(() => base[(Math.random() * base.length) | 0])
            .join("");
    };

    return generator(base, length);
};
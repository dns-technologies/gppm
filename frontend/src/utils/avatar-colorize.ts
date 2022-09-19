const database_colors = [
  "#2196F3",
  "#90CAF9",
  "#64B5F6",
  "#42A5F5",
  "#1E88E5",
  "#1976D2",
  "#1565C0",
  "#0D47A1",
  "#82B1FF",
  "#448AFF",
  "#2979FF",
  "#2962FF",
];

const schema_colors = [
  "#C969F6",
  "#D328D6",
  "#C15AF0",
  "#A20AD0",
  "#AE6AC7",
  "#B835D8",
  "#A72DB7",
  "#E065CA",
  "#E038A2",
  "#AC2495",
  "#D27CE3",
  "#E52CF6",
];

const table_colors = [
  "#4D951D",
  "#18E03A",
  "#85CD7D",
  "#4E943C",
  "#61DF6E",
  "#5BB60B",
  "#02AF6D",
  "#96EA42",
  "#2A8B12",
  "#A0DEBA",
  "#6DB09D",
  "#1FD486",
];

function hashFnv32a(str: string): number {
  let i: number,
    l: number,
    hval = 0x811c9dc5;

  for (i = 0, l = str.length; i < l; i++) {
    hval ^= str.charCodeAt(i);
    hval += (hval << 1) + (hval << 4) + (hval << 7) + (hval << 8) + (hval << 24);
  }
  return hval >>> 0;
}

export function avatarCollor(str: string, colors: string[]): string {
  const length = colors.length;
  const color_index = hashFnv32a(str) % length;
  return colors[color_index];
}

export const avatarCollorDatabase = (str: string) => avatarCollor(str, database_colors);

export const avatarCollorSchema = (str: string) => avatarCollor(str, schema_colors);

export const avatarCollorTable = (str: string) => avatarCollor(str, table_colors);

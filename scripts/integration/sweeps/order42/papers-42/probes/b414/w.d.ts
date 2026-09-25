interface Widget {
  lazy: string;
  css: string;
  dyn: number;
  type: string;
  with(x: number): void;
}
declare var Widget: { new(): Widget };

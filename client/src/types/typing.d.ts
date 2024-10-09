// global access to these types
type Draw = {
  ctx: CanvasRenderingContext2D;
  currPoint: Point;
  prevPoint: Point | null;
};

type Point = {x: number; y: number};

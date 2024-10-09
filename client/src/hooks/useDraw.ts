import {useCallback, useEffect, useRef, useState} from 'react';

export const useDraw = (
  OnDraw: ({ctx, currPoint, prevPoint}: Draw) => void
) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const prevPoint = useRef<null | Point>(null);
  const [mouseDown, setMouseDown] = useState(false);

  const onMouseDown = () => setMouseDown(true);

  const onMouseUp = () => {
    setMouseDown(false);
    prevPoint.current = null; // Reset previous point on mouse up
  };

  const onMouseMove = useCallback((e: MouseEvent) => {
    if (!mouseDown) return;

    const currPoint = computePointInCanvas(e);
    const ctx = canvasRef.current?.getContext('2d');
    if (!currPoint || !ctx) return;

    OnDraw({ctx, currPoint, prevPoint: prevPoint.current});
    prevPoint.current = currPoint;
  }, [OnDraw,mouseDown]);

  const computePointInCanvas = (e: MouseEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    return {x, y};
  };

  const clear = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    canvas.style.background = 'black';
    // Attach event listeners to canvas for mouse movements
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mouseup', onMouseUp);

    // Cleanup event listeners on component unmount
    return () => {
      canvas.removeEventListener('mousemove', onMouseMove);
      canvas.removeEventListener('mousedown', onMouseDown);
      canvas.removeEventListener('mouseup', onMouseUp);
    };
  }, [onMouseMove]);

  return {canvasRef, clear};
};

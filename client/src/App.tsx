import {useEffect, useState} from 'react';
import {useDraw} from './hooks/useDraw';
import {colors} from './constants';
import axios from 'axios';
// import Draggable from 'react-draggable';

interface GeneratedResult {
  expression: string;
  answer: string;
}

// interface Response {
//   expr: string;
//   result: string;
//   assign: boolean;
// }

export default function App() {
  const [color, setColor] = useState<string>('#fff');
  const [reset, setReset] = useState(false);
  const [dictOfVars, setDictOfVars] = useState({});
  const [result, setResult] = useState<GeneratedResult>();
  
  const drawLine = ({prevPoint, currPoint, ctx}: Draw) => {
    const {x: currX, y: currY} = currPoint;
    const lineWidth = 5;
    const startPoint = prevPoint ?? currPoint;
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.moveTo(startPoint.x, startPoint.y);
    ctx.lineTo(currX, currY);
    ctx.stroke();

    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(startPoint.x, startPoint.y, 2, 0, 2 * Math.PI);
    ctx.fill();
  };
  const {canvasRef, clear} = useDraw(drawLine);

  const runRoute = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const res = await axios.post(
      `${import.meta.env.VITE_SERVER_URL}/api/v1/compute`,
      {
        image: canvas.toDataURL('image/png'),
        dict_of_vars: dictOfVars,
      }
    );
    const data =await res.data.data[0];
    console.log(data);
    
    setResult({expression: data.expr, answer: data.result});
    console.log(result);
    
  };

  useEffect(() => {
    const canvas = canvasRef.current;

    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight - canvas.offsetTop;
  }, [canvasRef]);

  useEffect(() => {
    if (reset) {
      clear();
      setLatexExpression([]);
      setResult(undefined);
      setDictOfVars({});
      setReset(false);
    }
  }, [reset, clear]);

  return (
    <div className="bg-black">
      <div className="flex gap-3 text-white justify-evenly z-10">
        <button
          onClick={() => setReset(true)}
          className="bg-red-600 rounded-full p-1 px-2"
        >
          Reset
        </button>
        <div className="grid grid-cols-12">
          {colors.map((item) => (
            <button
              style={{backgroundColor: item.code}}
              className="col-span-1 w-5 h-5"
              title={item.name}
              onClick={() => setColor(item.code)}
              key={item.name}
            ></button>
          ))}
        </div>
        <button
          onClick={runRoute}
          className="bg-green-600 rounded-full p-1 px-2"
        >
          Run
        </button>
      </div>

      <canvas ref={canvasRef} className="absolute w-full h-full" />
      {!reset && <div className="absolute text-white">{result?.expression}</div>}
      
    </div>
  );
}

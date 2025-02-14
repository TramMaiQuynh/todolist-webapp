// import React, { useState, useEffect } from 'react';
// import Square from './Square';

// const SquareBoard = () => {
//   const [rows, setRows] = useState([]); // Mảng lưu các hàng ô vuông

//   useEffect(() => {
//     // Tạo các hàng với số lượng ô vuông ngẫu nhiên
//     const newRows = Array.from({ length: 5 }, () => {
//       const numSquaresInRow = Math.floor(Math.random() * 5) + 1; // Tạo số ô ngẫu nhiên từ 1 đến 5
//       return Array.from({ length: numSquaresInRow }, (_, index) => index);
//     });
//     setRows(newRows);
//   }, []);

//   return (
//     <div className="squares-container">
//       {rows.map((row, rowIndex) => (
//         <div className="row" key={rowIndex}>
//           {row.map((square, index) => (
//             <Square key={index} index={square} hasTick={Math.random() < 0.3} />
//           ))}
//         </div>
//       ))}
//     </div>
//   );
// };

// export default SquareBoard;

import React, { useState, /*useEffect*/ } from 'react';  // Import useState và useEffect từ React
import Square from './Square';

const SquareBoard = () => {
  // Định nghĩa số lượng ô vuông cho mỗi hàng
  const rows = [
    { id: 1, count: 10, startPosition: 0 },  // Hàng 1 có 10 ô vuông, bắt đầu từ vị trí 0
    { id: 2, count: 4, startPosition: 2 },   // Hàng 2 có 4 ô vuông, bắt đầu từ vị trí 2
    { id: 3, count: 5, startPosition: 4 },   // Hàng 3 có 5 ô vuông, bắt đầu từ vị trí 4
    { id: 4, count: 7, startPosition: 2 },   // Hàng 4 có 7 ô vuông, bắt đầu từ vị trí 2
  ];

  const [ticks] = useState([3, 5, 10, 15, 20, 25]);  // Các ô có dấu tick tại các chỉ mục này

  //useEffect(() => {
    // // Thêm các dấu tick ngẫu nhiên
    // const newTicks = [
    //   Math.floor(Math.random() * 25),
    //   Math.floor(Math.random() * 25),
    //   Math.floor(Math.random() * 25),
    // ];
    // setTicks(newTicks);
  //}, []);

  return (
    <div className="squares-container">
      {rows.map((row, rowIndex) => (
        <div key={row.id} className="row">
          {Array.from({ length: row.count }, (_, index) => {
            const squareIndex = row.startPosition + index; // Thêm offset cho từng ô trong hàng
            return (
              <Square
                key={squareIndex}
                index={squareIndex}
                hasTick={ticks.includes(squareIndex)} // Kiểm tra ô vuông có dấu tick hay không
              />
            );
          })}
        </div>
      ))}
    </div>
  );
};

export default SquareBoard;

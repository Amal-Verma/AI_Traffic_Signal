function lineIntersect(x1, y1, x2, y2, x3, y3, x4, y4) {
  const denominator = (x4 - x3) * (y2 - y1) - (y4 - y3) * (x2 - x1);
  if (denominator === 0) return false; // Lines are parallel

  const t = ((x1 - x3) * (y4 - y3) - (y1 - y3) * (x4 - x3)) / denominator;
  const u = -((x1 - x3) * (y2 - y1) - (y1 - y3) * (x2 - x1)) / denominator;

  return t >= 0 && t <= 1 && u >= 0 && u <= 1;
}

// Define the specific diagonal of the static rectangle
function getDiagonal(rect, diagonalType) {
  if (diagonalType === 'primary') {
    // Primary diagonal: top-left to bottom-right
    return { x1: rect.x, y1: rect.y, x2: rect.x + rect.width, y2: rect.y + rect.height };
  } else if (diagonalType === 'secondary') {
    // Secondary diagonal: top-right to bottom-left
    return { x1: rect.x + rect.width, y1: rect.y, x2: rect.x, y2: rect.y + rect.height };
  } else {
    throw new Error('Invalid diagonal type. Use "primary" or "secondary".');
  }
}

// Function to check collision between a diagonal of the static rectangle and the moving rectangle
function checkDiagonalCollisionWithMovingRect(staticRect, diagonalType, movingRect) {
  const diagonal = getDiagonal(staticRect, diagonalType);

  const rectEdges = [
    { x1: movingRect.x, y1: movingRect.y, x2: movingRect.x + movingRect.width, y2: movingRect.y }, // top
    { x1: movingRect.x + movingRect.width, y1: movingRect.y, x2: movingRect.x + movingRect.width, y2: movingRect.y + movingRect.height }, // right
    { x1: movingRect.x, y1: movingRect.y + movingRect.height, x2: movingRect.x + movingRect.width, y2: movingRect.y + movingRect.height }, // bottom
    { x1: movingRect.x, y1: movingRect.y, x2: movingRect.x, y2: movingRect.y + movingRect.height } // left
  ];

  // Check if any edge of the moving rectangle intersects with the diagonal of the static rectangle
  for (const edge of rectEdges) {
    if (lineIntersect(diagonal.x1, diagonal.y1, diagonal.x2, diagonal.y2, edge.x1, edge.y1, edge.x2, edge.y2)) {
      return true;
    }
  }

  return false;
}

export default checkDiagonalCollisionWithMovingRect;
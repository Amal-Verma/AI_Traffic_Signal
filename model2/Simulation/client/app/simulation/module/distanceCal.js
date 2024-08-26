// Function to calculate the distance from a point to a finite line segment
function pointToSegmentDistance(px, py, x1, y1, x2, y2) {
  const lineLengthSquared = (x2 - x1) ** 2 + (y2 - y1) ** 2;
  if (lineLengthSquared === 0) return Math.sqrt((px - x1) ** 2 + (py - y1) ** 2); // Line segment is a point

  let t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / lineLengthSquared;
  t = Math.max(0, Math.min(1, t));

  const closestX = x1 + t * (x2 - x1);
  const closestY = y1 + t * (y2 - y1);

  return Math.sqrt((px - closestX) ** 2 + (py - closestY) ** 2);
}

// Function to calculate the distance of a rectangle from a finite parallel line segment
export function rectangleToFiniteLineDistance(rect, lineX1, lineY1, lineX2, lineY2) {
  const distances = [
    pointToSegmentDistance(rect.x, rect.y, lineX1, lineY1, lineX2, lineY2),
    pointToSegmentDistance(rect.x + rect.width, rect.y, lineX1, lineY1, lineX2, lineY2),
    pointToSegmentDistance(rect.x, rect.y + rect.height, lineX1, lineY1, lineX2, lineY2),
    pointToSegmentDistance(rect.x + rect.width, rect.y + rect.height, lineX1, lineY1, lineX2, lineY2)
  ];
  return Math.min(...distances); // Return the smallest distance
}

// Function to calculate the distance between two rectangles
export function rectanglesDistance(rect1, rect2) {
  const rect1Edges = [
    { x1: rect1.x, y1: rect1.y, x2: rect1.x + rect1.width, y2: rect1.y }, // Top
    { x1: rect1.x + rect1.width, y1: rect1.y, x2: rect1.x + rect1.width, y2: rect1.y + rect1.height }, // Right
    { x1: rect1.x, y1: rect1.y + rect1.height, x2: rect1.x + rect1.width, y2: rect1.y + rect1.height }, // Bottom
    { x1: rect1.x, y1: rect1.y, x2: rect1.x, y2: rect1.y + rect1.height } // Left
  ];

  const rect2Edges = [
    { x1: rect2.x, y1: rect2.y, x2: rect2.x + rect2.width, y2: rect2.y }, // Top
    { x1: rect2.x + rect2.width, y1: rect2.y, x2: rect2.x + rect2.width, y2: rect2.y + rect2.height }, // Right
    { x1: rect2.x, y1: rect2.y + rect2.height, x2: rect2.x + rect2.width, y2: rect2.y + rect2.height }, // Bottom
    { x1: rect2.x, y1: rect2.y, x2: rect2.x, y2: rect2.y + rect2.height } // Left
  ];

  let minDistance = Infinity;

  for (const edge1 of rect1Edges) {
    for (const edge2 of rect2Edges) {
      const distance1 = pointToSegmentDistance(edge1.x1, edge1.y1, edge2.x1, edge2.y1, edge2.x2, edge2.y2);
      const distance2 = pointToSegmentDistance(edge1.x2, edge1.y2, edge2.x1, edge2.y1, edge2.x2, edge2.y2);
      const distance3 = pointToSegmentDistance(edge2.x1, edge2.y1, edge1.x1, edge1.y1, edge1.x2, edge1.y2);
      const distance4 = pointToSegmentDistance(edge2.x2, edge2.y2, edge1.x1, edge1.y1, edge1.x2, edge1.y2);

      const minEdgeDistance = Math.min(distance1, distance2, distance3, distance4);
      minDistance = Math.min(minDistance, minEdgeDistance);
    }
  }

  return minDistance;
}



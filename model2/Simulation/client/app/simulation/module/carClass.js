import checkDiagonalCollisionWithMovingRect from './diagonalIntersection.js'

// direction
// 1: up
// 2: left
// 3: down
// 4: right

export class Car {
  constructor (world, x, y, startDirection, endDirection) {
    this.world = world
    this.width = this.world.unit * 1
    this.height = this.world.unit * 2

    this.x = x
    this.y = y
    this.startDirection = startDirection
    this.endDirection = endDirection

    this.minThershold = 0.1 * this.world.unit
    this.maxThershold = 0.5 * this.world.unit

    this.speed = 2
    this.rotateonce = true

    if (this.startDirection === 2 || this.startDirection === 4) {
      this.width = this.world.unit * 2
      this.height = this.world.unit * 1
    }
  }

  rotate() {
    let temp = this.height;
    this.height = this.width;
    this.width = temp;
  }

  update() {

    const collision = checkDiagonalCollisionWithMovingRect(this.world.rect, 'primary', this)

    // console.log(collision)

    if (collision && this.rotateonce) {
      for (let i = 0; i < Math.abs(this.startDirection - this.endDirection); i++) {
        this.rotate()
      }
      this.rotateonce = false

      if (this.startDirection === 1) {
        this.y += this.speed
      }
      else if (this.startDirection === 2) {
        this.x += this.speed
      }
      else if (this.startDirection === 3) {
        this.y -= this.speed
      }
      else if (this.startDirection === 4) {
        this.x -= this.speed
      }

      this.startDirection = this.endDirection
    }

    if (this.startDirection === 1) {
      this.y -= this.speed
    }
    else if (this.startDirection === 2) {
      this.x -= this.speed
    }
    else if (this.startDirection === 3) {
      this.y += this.speed
    }
    else if (this.startDirection === 4) {
      this.x += this.speed
    }
  }

  draw(context) {
    context.fillStyle = 'red'
    context.fillRect(this.x, this.y, this.width, this.height)
  }
}
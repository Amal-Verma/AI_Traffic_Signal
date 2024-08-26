import { Car } from './carClass.js'

export class CarCollection {
  constructor (world) {
    this.world = world
    this.cars = []
    this.interval = 1000
    this.counter = 950
  }

  addCar (x, y, startDirection, endDirection) {
    this.cars.push(new Car(this.world, x, y, startDirection, endDirection))
  }

  update () {
    this.counter++

    // console.log(this.counter)
    if (this.counter % this.interval === 0) {
      this.addCar(this.world.width /2 - this.world.R3/2,this.world.height , 1, 4)
    }
    this.cars.forEach(car => {
      car.update()
    })
  }

  draw (context) {
    this.cars.forEach(car => {
      car.draw(context)
    })
  }
}
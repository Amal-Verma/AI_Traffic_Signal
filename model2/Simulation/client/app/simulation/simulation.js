'use client'

import React, {useEffect, useRef} from 'react'
import { CarCollection } from './module/carCollectionClass'

const Simulation = ({R1, R2, R3, R4}) => {

  const canvasStyle = {
    width: '100%',
    height: '100%',
    position: 'absolute',
    top: 0,
    left: 0,
    zIndex: 0,
    backgroundColor: 'lightblue'
  }

  const canvas = useRef(null)
  const roadEdgeColor = 'white'

  

  useEffect(() => {

    console.log(canvas.current)
    const loadCanvas = () => {
      const canvas = document.querySelector('canvas')
      const ctx = canvas.getContext('2d')
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight

      class World {
        constructor(width, height, R1, R2, R3, R4) {
          this.width = width
          this.height = height
          this.unit = this.width / 100

          this.R1 = R1
          this.R2 = R2
          this.R3 = R3
          this.R4 = R4
          this.roadCenterWidth = Math.max(this.R1, this.R3)
          this.roadCenterHeight = Math.max(this.R2, this.R4) 

          this.offset = 50
          this.edgeOffset = 5
          this.signalLinewidth = 2

          this.roadColor = 'black'
          
          this.carCollection = new CarCollection(this)

          this.rect = {x: this.width / 2 - this.roadCenterWidth / 2,
                  y: this.height / 2 - this.roadCenterHeight / 2,
                  width: this.roadCenterWidth,
                  height: this.roadCenterHeight
          }

          this.signalLines = [{x1 : this.width / 2 - this.roadCenterWidth / 2,
                              y1: this.height / 2 + this.roadCenterHeight / 2,
                              x2: this.width / 2 - this.roadCenterWidth / 2,
                              y2: this.height / 2 + this.edgeOffset / 2},

                              {x1 : this.width / 2 - this.roadCenterWidth / 2,
                              y1: this.height / 2 - this.roadCenterHeight / 2,
                              x2: this.width / 2 - this.roadCenterWidth / 2,
                              y2: this.height / 2 - this.edgeOffset / 2},
                              
                              {x1 : this.width / 2 - this.roadCenterWidth / 2,
                              y1: this.height / 2 - this.roadCenterHeight / 2,
                              x2: this.width / 2 - this.edgeOffset / 2,
                              y2: this.height / 2 - this.roadCenterHeight / 2},

                              {x1 : this.width / 2 + this.roadCenterWidth / 2,
                              y1: this.height / 2 - this.roadCenterHeight / 2,
                              x2: this.width / 2 + this.edgeOffset / 2,
                              y2: this.height / 2 - this.roadCenterHeight / 2},

                              {x1 : this.width / 2 + this.roadCenterWidth / 2,
                              y1: this.height / 2 - this.roadCenterHeight / 2,
                              x2: this.width / 2 + this.roadCenterWidth / 2,
                              y2: this.height / 2 - this.edgeOffset / 2},

                              {x1 : this.width / 2 + this.roadCenterWidth / 2,
                              y1: this.height / 2 + this.roadCenterHeight / 2,
                              x2: this.width / 2 + this.roadCenterWidth / 2,
                              y2: this.height / 2 + this.edgeOffset / 2},
                              

                              {x1 : this.width / 2 + this.roadCenterWidth / 2,
                              y1: this.height / 2 + this.roadCenterHeight / 2,
                              x2: this.width / 2 + this.edgeOffset / 2,
                              y2: this.height / 2 + this.roadCenterHeight / 2},

                              

                              {x1 : this.width / 2 - this.roadCenterWidth / 2,
                              y1: this.height / 2 + this.roadCenterHeight / 2,
                              x2: this.width / 2 - this.edgeOffset / 2,
                              y2: this.height / 2 + this.roadCenterHeight / 2},
          ]

          this.signalState = [1, 0, 0, 0, 0, 0, 0, 1]

          this.current = this.signalLines.length - 1

          this.interval = 20
          this.counter = 0
          
        }

        update() {
          this.carCollection.update()

          // if (this.counter < this.interval) {
          //   this.counter++
          //   return
          // }

          // this.counter = 0

          // this.signalState[this.current] = 0
          // this.current = (this.current + 1) % this.signalState.length
          // this.signalState[this.current] = 1

        }

        draw(context) {
          context.fillStyle = this.roadColor

          // road center
          context.fillRect(this.rect.x, this.rect.y, this.rect.width, this.rect.height)
    
          // left road R1
          context.fillRect(-this.offset, this.height / 2 - this.R2 / 2, this.width / 2 - this.roadCenterWidth / 2 + this.offset, this.R2)
    
          // right road R3
          context.fillRect(this.width / 2 + this.roadCenterWidth / 2, this.height / 2 - this.R4 / 2, this.width / 2 - this.roadCenterWidth / 2 + this.offset, this.R4)
    
          // top road R2
          context.fillRect(this.width / 2 - this.R1 / 2, -this.offset, R1, this.height / 2 - this.roadCenterHeight / 2 + this.offset)
    
          // bottom road R4
          ctx.fillRect(this.width / 2 - this.R3 / 2, this.height / 2 + this.roadCenterHeight / 2, this.R3, this.height / 2 - this.roadCenterHeight / 2 + this.offset)

          context.fillStyle = roadEdgeColor
          // left middle and side edge
          context.fillRect(-this.offset, this.height / 2 - this.edgeOffset / 2, this.width / 2 - this.roadCenterWidth / 2 + this.offset, this.edgeOffset)
          
          context.fillRect(-this.offset, this.height / 2 - this.R2/2 - this.edgeOffset, this.width / 2 - this.roadCenterWidth / 2 + this.offset, this.edgeOffset)
          context.fillRect(-this.offset, this.height / 2 + this.R2/2, this.width / 2 - this.roadCenterWidth / 2 + this.offset, this.edgeOffset)

          // right middle and side edge
          context.fillRect(this.width / 2 + this.roadCenterWidth / 2, this.height / 2 - this.edgeOffset / 2, this.width / 2 - this.roadCenterWidth / 2 + this.offset, this.edgeOffset)

          context.fillRect(this.width / 2 + this.roadCenterWidth / 2, this.height / 2 - this.R4/2 - this.edgeOffset, this.width / 2 - this.roadCenterWidth / 2 + this.offset, this.edgeOffset)
          context.fillRect(this.width / 2 + this.roadCenterWidth / 2, this.height / 2 + this.R4/2, this.width / 2 - this.roadCenterWidth / 2 + this.offset, this.edgeOffset)

          // top middle and side edge
          context.fillRect(this.width / 2 - this.edgeOffset / 2, -this.offset, this.edgeOffset, this.height / 2 - this.roadCenterHeight / 2 + this.offset)

          context.fillRect(this.width / 2 - this.R1/2 - this.edgeOffset, -this.offset, this.edgeOffset, this.height / 2 - this.roadCenterHeight / 2 + this.offset)
          context.fillRect(this.width / 2 + this.R1/2, -this.offset, this.edgeOffset, this.height / 2 - this.roadCenterHeight / 2 + this.offset)

          // bottom middle and side edge
          context.fillRect(this.width / 2 - this.edgeOffset / 2, this.height / 2 + this.roadCenterHeight / 2, this.edgeOffset, this.height / 2 - this.roadCenterHeight / 2 + this.offset)

          context.fillRect(this.width / 2 - this.R3/2 - this.edgeOffset, this.height / 2 + this.roadCenterHeight / 2, this.edgeOffset, this.height / 2 - this.roadCenterHeight / 2 + this.offset)
          context.fillRect(this.width / 2 + this.R3/2, this.height / 2 + this.roadCenterHeight / 2, this.edgeOffset, this.height / 2 - this.roadCenterHeight / 2 + this.offset)
          


          // Cars

          this.carCollection.draw(context)

          // signal lines

          this.signalLines.forEach((line, index) => {
            context.lineWidth = this.signalLinewidth
            context.strokeStyle = this.signalState[index] ? 'green' : 'red'
            // console.log(this.signalState[index])
            context.beginPath()
            context.moveTo(line.x1, line.y1)
            context.lineTo(line.x2, line.y2)
            context.stroke()
          })
        }
      }
      
      const world = new World(canvas.width, canvas.height, R1, R2, R3, R4)

      function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        world.update()
        world.draw(ctx)
        requestAnimationFrame(animate)
      }

      animate()

    }

    loadCanvas()
  }, [])

  return (
    <canvas style = {canvasStyle} ref = {canvas}/>
  )
}

export default Simulation
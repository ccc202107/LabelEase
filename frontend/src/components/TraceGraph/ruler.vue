<template>
  <div class="trace-graph-ruler">
    <div class="scale-list">
      <div v-for="(margin, index) in marginList"
            :key="index"
            :style="{'margin-right': margin + 'px'}"
            class="scale">
        <div class="number">{{scale * index >= 1000? scale * index / 1000 + 's': scale * index}}</div>
        <div class="column-line"></div>
      </div>
      <div class="column-line"></div>
    </div>
    <div class="row-line"></div>
  </div>
</template>

<script>
export default {
  name: 'TraceGraphRuler',
  props: {
    length: Number
  },
  data () {
    return {
      scaleList: [1, 2, 5, 10, 20, 50, 100, 200, 500],
      scale: 1,
      marginList: []
    }
  },
  created () {
    this.getScale()
    this.getMarginList()
  },
  methods: {
    getScale () {
      console.log(this.length)
      this.scaleList.forEach((item) => {
        if (this.length / item > 5) {
          this.scale = item
        }
      })
    },
    getMarginList () {
      this.marginList = []
      for (var i = 0; i < Math.floor(this.length / this.scale) + 1; i++) {
        if (i !== Math.floor(this.length / this.scale)) {
          this.$set(
            this.marginList,
            this.marginList.length,
            (this.scale / this.length) * 350 - 30
          )
        } else {
          this.$set(
            this.marginList,
            this.marginList.length,
            ((this.length - i * this.scale) / this.length) * 350 - 15
          )
        }
      }
    }
  },
  watch: {
    length () {
      this.getScale()
      this.getMarginList()
    }
  }
}
</script>

<style scoped>
.trace-graph-ruler {
  width: 380px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.scale-list {
  display: flex;
  width: 380px;
  align-items: flex-end;
}

.scale {
  width: 40px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.number {
  font-size: 10px;
}

.column-line {
  height: 6px;
  width: 1px;
  background-color: #7d8893;
}

.row-line {
  width: 350px;
  border-bottom: 1px solid #7d8893;
}
</style>

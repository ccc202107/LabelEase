<template>
  <div class="main">
    <div class="left-container">
      <div class="list-head">Time Period List</div>
      <div class="menu-box">
        <div v-for="(period, index) in periodList"
             :key="index"
             :class="{ activeCss: index == selectedIndex }"
             class="menu-item"
             @click="selectPeriod(index)"
             :style="'color:' + getMenuColor(index)">
          {{ period[0] }} - {{ period[1] }}
        </div>
      </div>
      <div class="menu-button-box">
        <el-button type="primary"
                   @click="exportGroundtruth"
                   plain
                   :disabled="init_flag == 0"
                   round>export groundtruth</el-button>
        <div class="button-note"
             v-if="init_flag == 0">
          Only after all anomaly periods have been labeled can export
          groundtruth.
        </div>
      </div>
    </div>

    <div class="center-container">
      <div class="topology-container">
        <div ref="network"
             class="topomap"></div>
        <div class="topo-title">Microservices System Relationship Diagram</div>
        <div class="topo-note">
          The darker the color, the more likely it is the root cause. And red
          represents manually labeled root cause.
        </div>
        <div id="customTooltip"
             class="custom-tooltip"></div>
      </div>
    </div>

    <div class="right-container">
      <div class="right-container-item">
        <div class="list-head">Service Information</div>
        <div class="service-info-box">
          <div>
            service name: <span v-if="selectedNode">{{ selectedNode.service }}</span>
          </div>
          <div>
            suspicious score:
            <span v-if="selectedNode">{{ selectedNode.score }}</span>
          </div>
          <div>
            number of abnormal traces:
            <span v-if="selectedNode">{{ selectedNode.ef }}</span>
          </div>
          <div>
            period duration mean:
            <span v-if="selectedNode">{{
              selectedNode.period_duration_mean
            }}</span>
          </div>
          <div>
            period duration std:
            <span v-if="selectedNode">{{
              selectedNode.period_duration_std
            }}</span>
          </div>
          <div>
            total duration mean:
            <span v-if="selectedNode">{{
              selectedNode.total_duration_mean
            }}</span>
          </div>
          <div>
            total duration std:
            <span v-if="selectedNode">{{
              selectedNode.total_duration_std
            }}</span>
          </div>
        </div>
      </div>
      <el-divider></el-divider>
      <div class="right-container-item">
        <div class="list-head">Fault Type Labeling</div>
        <div class="dialog-box">
          <div>Please select the fault type:</div>
          <div>
            <el-radio-group v-model="radio">
              <el-radio :label="1">pod-failure</el-radio>
              <el-radio :label="2">memory</el-radio>
              <el-radio :label="3">cpu</el-radio>
              <el-radio :label="4">delay</el-radio>
              <el-radio :label="5">others</el-radio>
            </el-radio-group>

            <div v-if="radio === 5">
              <div>Please enter the other fault type:</div>
              <el-input v-model="otherFault"></el-input>
            </div>
          </div>

          <div>Determine whether to label the service as an root cause?</div>
        </div>

        <el-button type="primary"
                   @click="labelRootCause">Confirm</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { Network } from 'vis'
import {
  get_period,
  get_fscore_and_services,
  export_groundtruth,
} from '@/api/trace.js'
export default {
  data() {
    return {
      periodList: [],
      selectedIndex: 0,
      period2label: {},
      edges: [],
      nodes: [],

      radio: -1,
      radio2faulttype: {},
      otherFault: '',
      init_flag: 0,
      selectedNode: '',
      index2ratio:{},
    }
  },
  methods: {
    exportGroundtruth() {
      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)',
      })
      export_groundtruth({ params: this.period2label })
        .then((response) => {
          loading.close()
          const url = window.URL.createObjectURL(new Blob([response.data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', 'groundtruth.json')
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        })
        .catch((error) => {
          console.error('下载失败:', error)
          loading.close()
        })
    },

    labelRootCause() {
        if(this.selectedNode=="") {
        this.$message({
          message: 'please choose root cause~',
          type: 'warning',
        })
        }
      else if (this.radio == -1) {
        this.$message({
          message: 'please choose fault type~',
          type: 'warning',
        })
      } else if (this.radio == 5 && this.otherFault == '') {
        this.$message({
          message: 'please enter fault type~',
          type: 'warning',
        })
      } else {
        
        this.period2label[this.selectedIndex] = []
        this.period2label[this.selectedIndex].push(this.selectedNode.service)
        this.radio2faulttype[5] = this.otherFault
        this.period2label[this.selectedIndex].push(
          this.radio2faulttype[this.radio]
        )
        if (Object.keys(this.period2label).length == this.periodList.length) {
          this.init_flag = 1
        }
        if(this.radio!=5) {
            this.index2ratio[this.selectedIndex] = this.radio
        }
        else {
            this.index2ratio[this.selectedIndex] = this.radio2faulttype[this.radio]
        }

        this.selectedIndex += 1
        if (this.selectedIndex >= this.periodList.length) this.selectedIndex = 0
        this.selectPeriod(this.selectedIndex)
      }
    },
    getMenuColor(index) {
      if (this.period2label[index]) return 'red'
      else return 'black'
    },
    selectPeriod(index) {
        this.radio=-1
        this.otherFault=''
        this.selectedNode=""
      this.selectedIndex = index
      if(this.index2ratio[this.selectedIndex]){
        if(this.index2ratio[this.selectedIndex] in [1,2,3,4]) this.radio=this.index2ratio[this.selectedIndex]
        else{
            this.radio=5
            this.otherFault=this.index2ratio[this.selectedIndex]
        }
      }
      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)',
      })
      get_fscore_and_services({ index: index })
        .then((res) => {
          loading.close()
          this.nodes = res.data.nodes
          this.edges = res.data.edges

          this.createTopology()
        })
        .catch((error) => {
          console.error(error)
          loading.close()
        })
    },
    createTopology() {
      var root_cause
      if (this.period2label[this.selectedIndex]) {
        root_cause = this.period2label[this.selectedIndex][0]
        for (var i = 0; i < this.nodes.length; i++) {
          if (this.nodes[i].service == root_cause) this.nodes[i]['color'] = 'red'
        }
      }

      const container = this.$refs.network
      const data = {
        nodes: this.nodes,
        edges: this.edges,
      }

      const options = {
        nodes: {
          font: {
            size: 20,
          },
          color: {},
          widthConstraint: {
            maximum: 170,
            minimum: 170,
          },
        },
        edges: {
          length: 500,
          color: {
            color: 'rgb(97, 168, 224)',
            highlight: 'rgb(97, 168, 224)',
            hover: 'red',
            inherit: 'from',
            opacity: 1.0,
          },
          font: {
            align: 'top',
          },
          smooth: true,
          arrows: { to: true },
        },
        interaction: {
          navigationButtons: true,
          hover: true,
          selectConnectedEdges: false,
        },
        manipulation: {
          enabled: false,
        },
        physics: {
          barnesHut: {
            springConstant: 0,
            // avoidOverlap: 0.2,
          },
        },
      }

      const network = new Network(container, data, options)

      var that = this
      network.on('click', function (params) {
        const { nodes } = params
        if (nodes.length > 0) {
          var nodeId = nodes[0]
          var nodeDetails
          for (let i = 0; i < data.nodes.length; i++) {
            if (data.nodes[i].id === nodeId) {
              nodeDetails = data.nodes[i]
              break
            }
          }
          that.selectedNode = nodeDetails
        }
      })

      network.on('blurNode', function () {
        var customTooltip = document.getElementById('customTooltip')
        customTooltip.style.display = 'none'
      })
    },
  },
  mounted() {
    get_period().then((res) => {
      this.periodList = res.data
      this.selectPeriod(0)
    })

    this.radio2faulttype[1] = 'pod-failure'
    this.radio2faulttype[2] = 'memory'
    this.radio2faulttype[3] = 'cpu'
    this.radio2faulttype[4] = 'delay'
  },
}
</script>

<style scoped>
.main {
  display: flex;
  justify-content: space-between;
  width: 100%;
  height: 96vh;
  margin: 0;
  padding: 0;
  background-color: white;
  font-size: 2rem;
}
.left-container {
  width: 27%;
  border: 1px solid black;
  border-radius: 8px;
}
.center-container {
  width: 40%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px black solid;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.right-container {
  width: 31%;
  border: 1px solid black;
  border-radius: 8px;
}
.menu-button-box {
  margin-top: 1.5rem;
}
.el-button {
  font-size: 1.6rem;
  margin-bottom: 1rem;
  width: 250px;
}
.button-note {
  font-size: 1.5rem;
  color: rgb(246, 80, 80);
}
.list-head {
  text-align: left;
  margin: 1rem;
}
.menu-item {
  width: 100%;
  white-space: nowrap;

  overflow: hidden;

  font-size: 1.5rem;
  color: #555555;
  background-color: white;
  padding-top: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #ccc;
}

.activeCss {
  background-color: rgb(209, 233, 250);
}

.menu-item:hover {
  background-color: rgb(209, 233, 250);
  border-color: rgb(233, 246, 255);
  cursor: pointer;
}
.menu-box {
  overflow: auto;
  height: 75%;
}

.topology-container {
  position: relative;
  width: 100%;
  height: 100%;
}
.topomap {
  width: 100%;
  height: 100%;
  position: relative;
}
.topo-title {
  position: absolute;
  top: 1rem;
  left: 1rem;
  
}
.topo-note {
  position: absolute;
  top: 60px;
  left: 1rem;
  color: rgb(139, 139, 139);
  font-size: 1.7rem;
  text-align: left;
}
.topo-icon {
  position: absolute;
  top: 20px;
  left: 0px;
  width: 2px;
  background-color: rgb(89, 163, 253);
}
.custom-tooltip {
  position: absolute;
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
  display: none;
  background-color: rgb(255, 255, 255);
}
.dialog-box div {
  margin: 10px;
  font-size: 1.9rem;
  text-align: left;
}

.el-radio /deep/ .el-radio__label {
  font-size: 1.9rem;
  line-height: 2;
}
.el-radio /deep/ .el-radio__inner {
  width: 20px;
  height: 20px;
  margin-bottom: 5px;

}

.service-info-box {
  text-align: left;
  margin-left: 2rem;
}
.service-info-box div {
  margin: 0.6rem;
}
.service-info-box div span {
  color: cornflowerblue;
}
</style>

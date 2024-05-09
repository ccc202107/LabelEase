<template>
  <div class="main">
    <div class="left-container">
      <div class="list-head">Trace List</div>
      <div class="menu-box">
        <div
          v-for="(traceId, index) in traceList"
          :key="index"
          :class="{ activeCss: index == selectedIndex }"
          class="menu-item"
          @click="selectTrace(traceId[0], index)"
          :style="'color:' + getMenuColor(traceId[0])"
        >
          {{ traceId[1] }}
        </div>
      </div>
      <div class="menu-button-box">
        <el-button
        class="list-button"
          type="primary"
          @click="exportLabel"
          plain
          :disabled="init_flag == 0"
          round
          >export labels</el-button
        >
        <br />
        <el-popover
          placement="bottom-end"
          trigger="hover"
        >
        <div class="popover-note">go to root cause localization task</div>
          <el-button
          class="list-button"
            type="primary"
            @click="toRCL"
            :disabled="init_flag != 2"
            plain
            round
            slot="reference"
            >root cause</el-button
          >
        </el-popover>

        <div class="button-note" v-if="init_flag == 0">
          Only after all traces have been labeled can subsequent tasks be
          performed.
        </div>
      </div>
    </div>

    <div class="right-container">
      <div class="topology-container">
        <div class="topo-title">Topological Relationship Diagram</div>
        <div class="topo-icon"></div>
        <div ref="network" class="topomap"></div>
        
        <div class="topo-button-box">
          <el-button type="primary" @click="labelAnomaly(0)" round class="topo-button"
            >Normal</el-button
          >
          <el-button type="primary" @click="labelAnomaly(1)" round class="topo-button"
            >Abnormal</el-button
          >
        </div>
        <div id="customTooltip" class="custom-tooltip"></div>
      </div>
      <div class="ganttchart-container">
        <trace-graph :id="selectedTraceId" />
      </div>
    </div>
  </div>
</template>

<script>
import { Network } from "vis";
import TraceGraph from "@/components/TraceGraph/index.vue";
import {
  get_topo_data,
  export_labels,
  get_trace_list,
  anomaly_period
} from "@/api/trace.js";
export default {
  components: {
    TraceGraph
  },
  data() {
    return {
      traceList: [],
      nodes: [],
      edges: [],
      selectedTraceId: "",
      selectedIndex: 0,
      traceId2label: {},
      labeledSet: new Set(),
      init_flag: 0
    };
  },
  methods: {
    exportLabel() {
      const loading = this.$loading({
        lock: true,
        text: "Loading",
        spinner: "el-icon-loading",
        background: "rgba(0, 0, 0, 0.7)"
      });
      export_labels({ params: this.traceId2label })
        .then(response => {
          loading.close();
          this.init_flag = 2;
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", "trace_labels.csv");
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        })
        .catch(error => {
          console.error("下载失败:", error);
          loading.close();
        });
    },
    toRCL() {
      const loading = this.$loading({
        lock: true,
        text: "Loading",
        spinner: "el-icon-loading",
        background: "rgba(0, 0, 0, 0.7)"
      });
      anomaly_period().then(res => {
        loading.close();
        this.$router.push("/LabelRootCause");
      });
    },
    labelAnomaly(label) {
      this.labeledSet.add(this.selectedTraceId);
      this.traceId2label[this.selectedTraceId] = label;
      this.selectedIndex += 1;
      if (this.selectedIndex >= this.traceList.length) this.selectedIndex = 0;
      this.selectTrace(
        this.traceList[this.selectedIndex][0],
        this.selectedIndex
      );
      if (this.labeledSet.size == this.traceList.length) this.init_flag = 1;
    },
    getMenuColor(traceId) {
      if (this.traceId2label[traceId] == 1) {
        return "red";
      } else if (this.traceId2label[traceId] == 0) {
        return "green";
      } else {
        return "black";
      }
    },
    selectTrace(trace_id, index) {
      this.selectedTraceId = trace_id;
      this.selectedIndex = index;
      get_topo_data({ trace_id: trace_id }).then(res => {
        this.nodes = res.data["nodes"];
        this.edges = res.data["edges"];
        this.createTopology();
      });
    },
    createTopology() {
      {
        // 创建拓扑图
        const container = this.$refs.network;
        const data = {
          nodes: this.nodes,
          edges: this.edges
        };

        const options = {
          nodes: {
            font: {
              size: 20
            },
            color: {},
            widthConstraint: {
              maximum: 120,
              minimum: 120
            }
          },
          edges: {
            length: 150,
            color: {
              color: "rgb(97, 168, 224)",
              highlight: "rgb(97, 168, 224)",
              hover: "red",
              inherit: "from",
              opacity: 1.0
            },
            font: {
              align: "top"
            },
            smooth: true,
            arrows: { to: true }
          },
          // layout: { randomSeed: 20 },
          interaction: {
            navigationButtons: true,
            hover: true,
            selectConnectedEdges: false
          },
          manipulation: {
            enabled: false
          },
                  physics: {
          barnesHut: {
            // springConstant: 0,
            // avoidOverlap: 0.2,
          },
        },
        };

        const network = new Network(container, data, options);

        network.on("click", function(params) {
          const { nodes } = params;
          if (nodes.length > 0) {
            var nodeId = nodes[0];
            var nodeDetails;
            for (let i = 0; i < data.nodes.length; i++) {
              if (data.nodes[i].id === nodeId) {
                nodeDetails = data.nodes[i];
                break;
              }
            }

            var customTooltip = document.getElementById("customTooltip");

            customTooltip.innerHTML =
              "<div>" +
              "<div>" +
              "Span id : " +
              nodeDetails["id"] +
              "</div>" +
              "<div>" +
              "Start time : " +
              nodeDetails["strat_time"] +
              "</div>" +
              "<div>" +
              "Service: " +
              nodeDetails["service_name"] +
              "</div>" +
              "<div>" +
              "Operation : " +
              nodeDetails["operation_name"] +
              "</div>" +
              "<div>" +
              "Status code: " +
              nodeDetails["status"] +
              "</div>" +
              "<div>" +
              "Duration : " +
              nodeDetails["duration"] +
              "μs" +
              "</div>" +
              "</div>";

            customTooltip.style.left = params.pointer.DOM.x + 10 + "px";
            customTooltip.style.top = params.pointer.DOM.y - 10 + "px";
            customTooltip.style.textAlign = "left";

            customTooltip.style.display = "block";
          }
        });

        network.on("blurNode", function() {
          var customTooltip = document.getElementById("customTooltip");
          customTooltip.style.display = "none";
        });
      }
    }
  },
  mounted() {
    get_trace_list().then(res => {
      this.traceList = res.data;
      this.selectTrace(this.traceList[0][0], 0);
    });
  }
};
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
  width: 30%;
  border: 1px solid black;
  border-radius: 8px;
}
.menu-button-box {
  margin-top: 1.5rem;
}
.el-button {
  font-size: 1.6rem;
  margin-bottom: 1rem;
  /* width: 150px; */
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
  height: 70%;
}
.right-container {
  width: 68%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.topology-container {
  position: relative;
  width: 100%;
  height: 48%;
  border: 1px black solid;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.ganttchart-container {
  width: 100%;
  height: 48%;
  overflow-y: auto;
  border: 1px black solid;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.topomap {
  width: 100%;
  height: 100%;
  position: relative;
}
.topo-button-box {
  position: absolute;
  bottom: 1em;
  right: 1em;
  display: flex;
  flex-direction: row-reverse;
  justify-content: space-between;
}
.topo-button-box button {
  margin-right: 1rem;
}
.topo-title {
  position: absolute;
  top: 1rem;
  right: 1rem;
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
  background-color: #fff;
}
.button-note {
  font-size: 1.4rem;
  color: rgb(246, 80, 80);
}
.list-button{
    width: 250px;
}
.topo-button{
    width: 150px;
}
.popover-note{
    font-size: 1.8rem;
}
</style>

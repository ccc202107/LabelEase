<template>
  <div class="trace-graph">
    <div class="graph-box">
      <div>
        <div class="title">{{operationName}}</div>
        <div class="trace-id">trace id: {{id}}</div>
        <div class="detail">
          <label-black value="Start Time"></label-black>
          <div style="margin-right: 10px;">{{startTime}}</div>
          <label-black value="Duration"></label-black>
          <div>{{duration}} us</div>
        </div>
      </div>
      <div class="tab-list">
        <el-button :type="tabIndex === 0? 'primary': 'info'"
                   @click="() => {this.tabIndex = 0}"
                   icon="el-icon-s-order">List</el-button>
        <el-button :type="tabIndex === 1? 'primary': 'info'"
                   @click="() => {this.tabIndex = 1}"
                   icon="el-icon-s-grid">Grid</el-button>
      </div>
    </div>
    <trace-graph-list v-if="tabIndex === 0"
                      :data="treeData"></trace-graph-list>
    <trace-graph-table v-if="tabIndex === 1"
                       :data="treeData"></trace-graph-table>
  </div>
</template>

<script>
import TraceGraphList from '@/components/TraceGraph/list.vue'
import TraceGraphTable from '@/components/TraceGraph/table.vue'
import LabelBlack from '@/components/Label/black.vue'
import { getTree, get_gantt_data } from '@/api/trace.js'
import { toHump } from '@/utils/hump-line-convert.js'

export default {
  name: 'TraceGraph',
  components: {
    TraceGraphList,
    TraceGraphTable,
    LabelBlack,
  },
  props: {
    id: String,
  },
  data() {
    return {
      tabIndex: 0,
      operationName: '',
      startTime: '',
      duration: '',
      treeData: [],
    }
  },

  methods: {},
  watch: {
    id(newVal) {
      get_gantt_data({ trace_id: this.id }).then((res) => {
        this.treeData = res.data
        this.operationName = res.data[0].operation_name
        this.startTime = res.data[0].startTime
        this.duration = res.data[0].duration
      })
    },
  },
}
</script>

<style scoped>
.trace-graph {
  padding: 10px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.trace-id {
  margin-bottom: 10px;
}

.detail {
  display: flex;
  align-items: center;
}

.el-button {
  padding: 10px;
  font-size: 1.8rem;
}
.graph-box {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 15px;
  border-bottom: 1px solid #eeeeee;
  font-size: 1.8rem;
}
</style>

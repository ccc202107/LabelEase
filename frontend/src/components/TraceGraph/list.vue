<template>
  <div class="custom-tree-container">
    <el-tree :data="data" @node-click="handleNodeClick" default-expand-all>
      <span class="custom-tree-node" slot-scope="{ data }">
        <el-tooltip
          :content="
            'The average latency under similar call paths is ' +
              data.call_path.mean +
              ', the standard deviation is ' +
              data.call_path.std +
              ', and the median is ' +
              data.call_path.median
          "
          placement="top"
        >
          <div class="item-box">
            <div
              class="bar"
              :style="'width:' + data.length * 1200 + 'px'"
            ></div>
            <div class="node-label-box">
              <div class="node-service">{{ data.cmdb_id }}</div>
              <div class="node-duration">{{ data.duration }}μs</div>
              <div class="node-operation">{{ data.operation_name }}</div>
            </div>
          </div>
        </el-tooltip>
      </span>
    </el-tree>
  </div>
</template>

<script>
export default {
  props: {
    data: Array
  },
  data() {
    return {};
  },
  mounted() {},
  watch: {},
  methods: {
    handleNodeClick(data) {
      console.log(data);
    }
  }
};
</script>
<style>
.custom-tree-container {
  font-size: 1.7rem;
}
.el-tree-node__content {
  height: 90px;
}

.bar {
  background-color: #57cf95;
  height: 1.8rem;
}

.node-label-box {
  /* text-align: left; */
  display: flex;
  margin-top: 0.5rem;
}
.node-label-box div {
  margin-right: 2.5rem;
}
.el-tooltip__popper {
  font-size: 1.7rem;
}
.item-box{
    width: 62vw;
    padding-bottom: 10px;
    border-bottom: 1px solid blanchedalmond;
}
.node-service{
    color: rgb(139, 138, 138);
}
.node-duration{
    color:cornflowerblue
}

</style>

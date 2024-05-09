<template>
  <div class='table-box'>
    <el-table 
              :data="data"
              row-key="id"
              style="font-size: 1.7rem"
              :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
              default-expand-all>
      <el-table-column label="Operation Name"
                       prop="operation_name"
                       width="750" />
      <el-table-column label="Duration(μs)"
                       prop="duration"
                       width="300" />
      <el-table-column label="Service"
                       prop="cmdb_id"
                       width="300" />
      <el-table-column label="Status Code"
                       prop="status_code"
                       width="200" align="center" />
    </el-table>
  </div>
</template>
<script>
export default {
  props: {
    data: Array,
  },
  data() {
    return {}
  },
  mounted() {},
  watch: {},
  methods: {},
}
</script>

<style scoped>
</style>
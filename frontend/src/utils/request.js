import axios from 'axios'

// create an axios instance
const service = axios.create({
  baseURL: 'http://localhost:8000/' // url = base url + request url
})

export default service

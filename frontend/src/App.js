// import "antd/dist/reset.css"
import {Col,Row,Timeline} from "antd"
import {CheckCircleOutlined, MinusCircleOutlined} from "@ant-design/icons"
import {useState, useEffect} from "react" 

function App() {
  const [tasks, setTasks] = useState([])
  const [timeline, setTimelines] = useState([])

  useEffect(()=>{
    const fetchAllTasks = async () => {
      const response = await fetch("http://localhost:8000/task/")
      const fetchedTasks = await response.json()
      setTasks(fetchedTasks)
    }
    const interval = setInterval(fetchAllTasks, 1000)
    
    return () => {
      clearInterval(interval)
    }
  }, [])

  useEffect(()=>{
    const timelineItems = tasks.map((task)=>{
      return task.completed ? (
        <Timeline>
          <Timeline.Item
              dot={<CheckCircleOutlined />}
              color = "green"
              style = {{textDecoration:"line-through", color:"green"}}
            >
              {task.name}
              <br/><small>{task.id}</small>
          </Timeline.Item>
        </Timeline>
      ):(
        <Timeline>
          <Timeline.Item
            dot={<CheckCircleOutlined />}
            color = "green"
            style = {{textDecoration:"line-through", color:"green"}}
          >
            {task.name}
            <br/><small>{task.id}</small>
          </Timeline.Item>
        </Timeline>
      )
    })
    setTimelines(timelineItems)
  },[])
  return (
    <div>
      <h2 style={{textAlign:"center"}}>Tasks</h2>
      <Row style = {{marginTop:50}}>
        <Col span={14} offset={5}>
          <Timeline mode='alternate'>
            {timeline}
          </Timeline>
        </Col>
      </Row>
    </div>
  );
}



export default App;

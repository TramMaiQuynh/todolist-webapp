import '/home/quynh-tram/SgodUTH/To_Do_list_web_app/Frontend/todo_frontend/src/AppPage.css';
import TaskItem from "/home/quynh-tram/SgodUTH/To_Do_list_web_app/Frontend/todo_frontend/src/components/TaskItem.js"; // Giả sử bạn có TaskItem để hiển thị danh sách task
import React, { useState, useEffect } from 'react';
// import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
// import axios from 'axios';

const AppPage = () => {
  // const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState("");  // State để lưu thông báo lỗi
  // State để lưu thông tin các categories và task
  const [categories, setCategories] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [taskData, setTaskData] = useState({
    title: '',
    description: '',
    status: 'Pending',
    priority: 'Medium',
    due_date: '',
    category: 0,
    // custom_category: '',
    is_important: false,
  });

  // Lấy danh mục từ backend khi component mount
  useEffect(() => {
    //Lay danh sach Categories
    fetch('http://127.0.0.1:8000/api/v1/categories/')
      .then((res) => {
        // Kiểm tra nếu phản hồi trả về có phải là JSON
        if (!res.ok) {
          throw new Error('Network response was not ok');
        }
        return res.json();
      })
      .then((data) => {
        setCategories(data.results || data); // Lấy danh sách categories từ field 'results'
      })
      .catch((error) => {
        console.error('Lỗi khi tải categories:', error);
        alert(`Error: ${error.message}`);
      });


    // Lấy danh sách tasks
    fetch('http://127.0.0.1:8000/api/v1/tasks/')
      .then((res) => res.json())
      .then((data) => setTasks(data.results || data))
      .catch((error) => {
        console.error('Lỗi khi tải tasks:', error);
        alert(`Error: ${error.message}`);
      });
    
  }, []);
  
    
  // Hàm xử lý khi input thay đổi
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTaskData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  // Hàm xử lý khi checkbox thay đổi
  const handleCheckboxChange = (e) => {
    const { name, checked } = e.target;
    setTaskData((prevData) => ({
      ...prevData,
      [name]: checked,
    }));
  };

  // Hàm xử lý submit form
  const handleSubmit = (e) => {
    e.preventDefault();

    console.log('Selected category value:', taskData.category);
    console.log('Category type:', typeof taskData.category);
    console.log('Category type:', typeof categories[0].id); 

    // Kiểm tra nếu không có due_date
    if (!taskData.due_date) {
      // setErrorMessage("Please select a due date for the task.");  // Hiển thị thông báo lỗi cụ thể
      toast.error("Please select a due date for the task.");  // Hiển thị thông báo lỗi cụ thể
      return;  // Dừng lại và không gửi yêu cầu tạo task nếu thiếu ngày
    }

    // Check if category is selected
    if (taskData.category === 0) {
      toast.error("Please select a category for the task.");  // Show toast error if category is not selected
      return;  // Prevent form submission
    }
    
    // Kiểm tra nếu ngày Due Date nhỏ hơn ngày hiện tại
    const today = new Date().toISOString().split("T")[0];
    // const dueDate = new Date(taskData.due_date).toISOString().split("T")[0];
    if (taskData.due_date < today) {  
      toast.error('Due date cannot be in the past.'); // Lưu thông báo lỗi
      return; // Dừng lại, không tiếp tục tạo task
    }       
    
    setErrorMessage("");  // Reset thông báo lỗi nếu form hợp lệ

    const payload = {
      ...taskData,
      description: taskData.description || '',  // Ensure description is included
      category: Number(taskData.category),  // Ensure category is sent as a number
    };
    // };

    console.log("Payload send to backend: ", typeof payload.category)
    
    // Gửi yêu cầu POST lên backend để tạo task mới
    fetch('http://127.0.0.1:8000/api/v1/tasks/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
    .then((res) => {
      if (!res.ok) {
        
        if (res.status === 400) {
          setErrorMessage('Invalid data provided.');
        } else {
          setErrorMessage('Server error, please try again.');
        }
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.json();
    })
    .then((data) => {
      // Task đã được tạo thành công, hiển thị thông báo
      console.log('Task created:', data);
      
      // setTasks((prevTasks) => [...prevTasks, data]); // Thêm task mới vào danh sách
      fetchData()
      // Có thể reset lại form hoặc hiển thị thông báo thành công
      setTaskData({
        title: '',
        description: '',
        status: 'Pending',
        priority: 'Medium',
        due_date: '',
        category: 0,
        custom_category: '',
        is_important: false,
      });
      
      // Thông báo thành công
      toast.success('Task created successfully!');
    })
    .catch((error) => {
      if (error.name === 'TypeError') {
        console.error('Network error:', error);
        toast.error('Network error, please check your connection.');
      } else {
        console.error('Error creating task:', error);
        toast.error('Unexpected error, please try again.');
      }
    });
  };

  const fetchData = async () => {
    try {
      const tasksResponse = await fetch('http://127.0.0.1:8000/api/v1/tasks/');
      const tasksData = await tasksResponse.json();
      setTasks(tasksData.results || tasksData);
      
      const categoriesResponse = await fetch('http://127.0.0.1:8000/api/v1/categories/');
      const categoriesData = await categoriesResponse.json();
      setCategories(categoriesData.results || categoriesData);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Error loading data, please try again.');
    }
  };

 
  // Hàm xóa task
  const handleDeleteTask = (taskId) => {
    fetchData() 
  };
  
  // Hàm cập nhật task (đánh dấu hoàn thành)
  const handleCompleteTask = (id) => {
    fetch(`http://127.0.0.1:8000/api/v1/tasks/${id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status: 'Completed' }),
    })
      .then((res) => {
        if (res.ok) {
          setTasks((prevTasks) =>
            prevTasks.map((task) =>
              task.id === id ? { ...task, status: 'Completed' } : task
            )
          );
          toast.success('Task marked as completed!');
        } else {
          toast.error('Error marking task as completed, please try again.');
        }
      })
      .catch((error) => {
        console.error('Error completing task:', error);
        toast.error('Error completing task, please try again.');
      });
  };

  // Hàm thanh lọc task theo status
  // const filterTasks = (status) => {
  //   fetch(`http://127.0.0.1:8000/api/v1/tasks/?status=${status}`)
  //     .then((res) => res.json())
  //     .then((data) => setTasks(data.results || data))
  //     .catch((error) => {
  //       console.error('Error filtering tasks:', error);
  //       alert(`Error: ${error.message}`);
  //     });
  // };  


  return (
    <div className="app-page">
      <div className="task-form">
        <h2>Create your new task</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Title:
            <input
              type="text"
              name="title"
              value={taskData.title}
              onChange={handleInputChange}
              placeholder='Enter task name'
              required
            />
          </label>

          <label>
            Description:
            <textarea
              type="text"
              name="description"
              value={taskData.description}
              onChange={handleInputChange}
              placeholder='Enter task description'
            />
          </label>

          <label>
            Status:
            <select
              name="status"
              value={taskData.status}
              onChange={handleInputChange}
            >
              <option value="Pending">Pending</option>
              <option value="In_progress">In Progress</option>
            </select>
          </label>

          <label>
            Priority:
            <select
              name="priority"
              value={taskData.priority}
              onChange={handleInputChange}
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          </label>

          <label>
            Due Date:
            <input
              type="date"
              name="due_date"
              value={taskData.due_date}
              onChange={handleInputChange}
            />
          </label>

          {errorMessage && <div className="error-message">{errorMessage}</div>} {/* Hiển thị thông báo lỗi */}

          <label>
            Category:
            <select
              name="category"
              value={taskData.category}
              onChange={handleInputChange}
            >
              <option value="">Select a category</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </label>

          {/* <label>
            Custom Category:
            <input
              type="text"
              name="custom_category"
              value={taskData.custom_category}
              onChange={handleInputChange}
              placeholder="Enter a custom category"
            />
          </label> */}

          <label>
            Is Important:
            <input
              type="checkbox"
              name="is_important"
              checked={taskData.is_important}
              onChange={handleCheckboxChange}
            />
          </label>     
                    
          <button type="submit">Create Task</button>
        </form>
      </div>

      <div className="task-list">
        <div className="task-header">
          <h3>Your Tasks</h3>
        </div>
        <ul className="task-items">
          {tasks.map((task) => (
            <TaskItem 
              key={task.id} 
              task={task}
              categories={categories} 
              onDelete={handleDeleteTask}
              onToggleComplete={handleCompleteTask} 
              onUpdate={fetchData}
            />
          ))}
        </ul>
      </div>
    </div>
  );
};

export default AppPage;

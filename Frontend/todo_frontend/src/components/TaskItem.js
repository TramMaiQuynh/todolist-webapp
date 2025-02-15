// 

import React, { useState, /*useEffect*/ } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../TaskItem.css';

const TaskItem = ({ task, onDelete, categories, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTask, setEditedTask] = useState({ ...task });
  
  const handleUpdate = (e) => {
    e.preventDefault();
    
    // Validate due date
    const today = new Date().toISOString().split("T")[0];
    if (editedTask.due_date < today) {
      toast.error('Due date cannot be in the past.');
      return;
    }

    const payload = {
      ...editedTask,
      category: editedTask.custom_category || editedTask.category,
    };

    axios.patch(`http://localhost:8000/api/v1/tasks/${task.id}/`, payload)
      .then((response) => {
        setIsEditing(false);
        toast.success("Task updated successfully!");
        // Add this line to refresh the task list
        if (typeof onUpdate === "function") {
          onUpdate();  // This will trigger the fetchData in AppPage
        }
      })
      .catch((error) => {
        console.error('Error updating task:', error);
        toast.error("Error updating task, please try again.");
      });
  };

  const handleDelete = () => {
    axios
      .delete(`http://localhost:8000/api/v1/tasks/${task.id}/`)
      .then(() => {
        if (typeof onDelete === "function") {
          onDelete(task.id);
        }
        toast.success("Task deleted successfully!");
      })
      .catch((error) => {
        console.error("Error deleting task:", error);
        toast.error("Error deleting task, please try again.");
      });
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setEditedTask(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="task-item">
      {isEditing ? (
        <form onSubmit={handleUpdate}>
          <label>
            Title:
            <input
              type="text"
              name="title"
              value={editedTask.title}
              onChange={handleInputChange}
              required
            />
          </label>

          <label>
            Description:
            <textarea
              name="description"
              value={editedTask.description}
              onChange={handleInputChange}
            />
          </label>

          <label>
            Status:
            <select
              name="status"
              value={editedTask.status}
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
              value={editedTask.priority}
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
              value={editedTask.due_date}
              onChange={handleInputChange}
            />
          </label>

          <label>
            Category:
            <select
              name="category"
              value={editedTask.category}
              onChange={handleInputChange}
            >
              <option value="">Select a category</option>
              {categories && categories.map((category) => (
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
              value={editedTask.custom_category || ''}
              onChange={handleInputChange}
              placeholder="Enter a custom category"
            />
          </label> */}

          <label>
            Is Important:
            <input
              type="checkbox"
              name="is_important"
              checked={editedTask.is_important}
              onChange={handleInputChange}
            />
          </label>

          <div>
            <button type="submit">Save Changes</button>
            <button type="button" onClick={() => setIsEditing(false)}>Cancel</button>
          </div>
        </form>
      ) : (
        <>
          <h3>{task.title}</h3>
          <p>{task.description}</p>
          <p>Status: {task.status}</p>
          <p>Due: {task.due_date}</p>
          <p>Priority: {task.priority}</p>
          <p>Category: { (categories?.find(cat => cat.id === task.category)?.name) || 
             'No category'}
            </p>          
          <p>Important: {task.is_important ? 'Yes' : 'No'}</p>
          <button onClick={() => setIsEditing(true)}>Edit</button>
          <button onClick={handleDelete}>Delete</button>
        </>
      )}
    </div>
  );
};

export default TaskItem;
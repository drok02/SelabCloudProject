import React, { Component } from 'react';
import Template from './components/Template';
import Form from './components/Form';
import ItemList from './components/ItemList';

class App extends Component {
  id = 3

  state = {
    input: '',
    todos: [
      {id: 0, text: '리액트 소개', checked: false },
      {id: 1, text: '리액트 소개', checked: true },
      {id: 2, text: '리액트 소개', checked: false }
    ]
  }

  handleChange = (e) => {
    this.setState({
      input: e.target.value //바뀔 input 값
    });
  }

  handleCreate = () => {
    const { input, todos } = this.state;
    this.setState({
      input: '', //인풋을 비워준 후 concat을 이용하여 배열에 추가
      todos: todos.concat({
        id: this.id++,
        text: input,
        checked: false
      })
    });
  }

  handleKeyPress = (e) => {
    if(e.key === 'Enter') { //Enter가 눌려지면 handleCreate 호출
      this.handleCreate();
    }
  }

  render() {
    const { input, todos } = this.state;
    const {
      handleCreate,
      handleChange,
      handleKeyPress
    } = this;

    return (
      <Template form={(
        <Form
          value={input}
          onKeyPress={handleKeyPress}
          onChange={handleChange}
          onCreate={handleCreate}
        />
      )}>
        <ItemList todos={todos}/>
      </Template>
    );
  }
}

export default App;
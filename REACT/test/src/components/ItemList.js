import React, { Component } from 'react';
import Item from './Item';
//todos: todo라는 객체들이 들어있는 배열, onToggle: 체크박스를 켜고 끄는 함수,
//onRemove: 아이템을 삭제시키는 함수
class ItemList extends Component {
    render() {
        const { todos, onToggle, onRemove} = this.props;

        const todoList = todos.map(
            ({id, text, checked}) => (
                <Item
                    id={id}
                    text={text}
                    checked={checked}
                    onToggle={onToggle}
                    onRemove={onRemove}
                    key={id}
                />
            )
        );

        return (
            <div>
                {todoList}
            </div>
        );
    }
}

export default ItemList;

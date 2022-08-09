import React, { Component } from 'react';
import './Item.css';

class Item extends Component {
    render() {
        const { text, checked, id, onToggle, onRemove} = this.props;
//checked: 체크박스 상태, onToggle: 체크박스 켜고 끄는 함수, onRemove: 아이템 삭제시키는 함수
        return (
            <div className="item" onClick={() => onToggle(id)}>
                <div className="remove" onClick={(e) => {
                    e.stopPropagation(); //onToggle이 실행되지 않도록 함(onRemove만 실행되게). 부모까지의 이벤트 확산을 멈춰주는 역할.
                    onRemove(id)} //id: todo의 고유 id
                }>&times;</div>
                <div className={`todo-text ${checked && 'checked'}`}>
                    <div>{text}</div>
                </div>
                {
                    checked && (<div className="check-mark">✓</div>)
                }
            </div>
        );
    }
}

export default Item;
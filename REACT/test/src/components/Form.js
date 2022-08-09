import React from 'react';
import './Form.css';
//value: 인풋 내용, onCreate: 버튼이 클릭될 때 실행될 함수,
//onChange: 인풋 내용이 변경될 때 실행될 함수, onKeyPress: 인풋에서 키를 입력할 때 실행될 함수(Enter가 눌렸을 때 onCreate한 것과 같은 효과를 내기 위해서 사용.)
const Form = ({value, onChange, onCreate, onKeyPress}) => {
    return (
        <div className="form">
            <input value={value} onChange={onChange} onKeyPress={onKeyPress}/>
            <div className="create-button" onClick={onCreate}>
                추가
            </div>
        </div>
    );
};

export default Form;
import React from 'react';
import './Template.css'; 

const Template = ({form, children}) => {
    return (
        <main className="template">
            <div className="title">
                오늘 할 일
            </div>
            <section className="form-wrapper">
                {form}
            </section>
            <section className="template-wrapper">
                {children}
            </section>
        </main>
    );
};

export default Template;

//함수형 컴포넌트임. form, children은 파라미터이고, 이들은 props라고 한다.
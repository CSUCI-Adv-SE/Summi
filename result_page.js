import React from 'react';
import ReactDOM from 'react-dom';
import './style.css';

class ConversionResult extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            text: ''
        };
    }

    componentDidMount() {
        // Make a request to our "Summi" server to get the converted text
        // and set it as the state of the component
        fetch('http://summi_url/converted-text')
            .then(response => response.text())
            .then(data => {
                this.setState({
                    text: data
                });
            })
            .catch(error => console.log(error));
    }

    render() {
        return (
            <div className="container">
                <div className="header">
                    <h1>PDF to Text Conversion Result</h1>
                </div>
                <div className="content">
                    <pre>{this.state.text}</pre>
                </div>
            </div>
        );
    }
}

ReactDOM.render(<ConversionResult />, document.getElementById('root'));
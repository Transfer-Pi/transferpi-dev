import React from "react";

import { Icon, icons } from "./icons";

import "./App.css";

let example_config = {
  subdomain: "vptl185",
  account_keys: {
    private: "0ccefce43ad790645ba50fe295c39909529f1869716f439186bcde32121c39fd",
    public: "87719e5b60268b5dcf2c32bc1838d9c6cdf4c47825ba61f7dee0f423aaf79b4b",
  },
  port: 2121,
  allowed_hosts: [],
  server_config: {
    remote: {
      host: "tpialpha.tk",
      port: 80,
    },
    local: {
      host: "localhost",
      port: 2121,
      n_pools: 5,
      chunk_size: 512,
    },
    web: {
      host: "https://transferpi.tk",
    },
  },
};

async function POST(
  options = {
    path: "/",
    data: {},
  }
) {
  let { path, data } = options;
  return await fetch({
    url: "http://localhost" + path,
    method: "POST",
    data: JSON.stringify(data),
  });
}

async function GET(
  options = {
    path: "/",
  }
) {
  return await fetch("http://localhost:2121" + options.path);
}

const Token = (props = { token: {} }) => {
  return (
    <div className="token-card">
      {Object.keys(props.token).map((key, i) => {
        return (
          <div className="row" key={i}>
            <div className="col">{key}</div>
            <div className="col">
              {props.token[key].toString().length > 48
                ? props.token[key].toString().slice(0, 48) + "..."
                : props.token[key].toString()}
            </div>
          </div>
        );
      })}
    </div>
  );
};

const Tokens = (props = { render: [] }) => {
  let { render } = props;
  return (
    <div className="tokens">
      {render.data.map((token, i) => {
        return <Token token={token} key={i} />;
      })}
    </div>
  );
};

const User = (props) => {
  return <div>Users</div>;
};

const App = (props) => {
  let [tokens, tokensState] = React.useState({
    data: [],
    isFetching: true,
  });

  let [render, renderTokens] = React.useState({
    ...tokens,
  });

  let [container, containerState] = React.useState("tokens");

  async function update() {
    await GET({
      path: "/file/GET_TOKENS",
    })
      .then((response) => response.json())
      .then((res) => {
        let { data } = res;
        if (window.tokens.data.length !== data.length) {
          window.tokensState({
            data: data,
            isFetching: false,
          });
          renderTokens({
            data: data,
            isFetching: false,
          });
        }
      });
  }

  function performSearch(e) {
    let data = tokens.data;
    if (e.target.value.length > 0) {
      data = data.filter((token) => {
        return token.filename.lastIndexOf(e.target.value) > -1;
      });
    }
    renderTokens({
      data: data,
      isFetching: true,
    });
  }

  function getRenderState() {
    switch (container) {
      case "tokens":
        return <Tokens render={render} />;
      case "user":
        return <User />;
      default:
        return <Tokens render={render} />;
    }
  }

  React.useEffect(async function () {
    window.tokens = tokens;
    window.tokensState = tokensState;
    if (window.__UPDATE__ === undefined) {
      update();
      clearInterval(window.__UPDATE__);
      window.__UPDATE__ = setInterval(update, 1000);
    }
  });

  return (
    <div className="app">
      <div className="header">
        <div className="head" onClick={(e) => containerState("tokens")}>
          <icons.Logo />
        </div>
        <div className="head">
          <icons.Search />
          <input placeholder="Search" onChange={performSearch} />
        </div>
        <div className="head">
          <icons.User onClick={(e) => containerState("user")} />
        </div>
      </div>
      {getRenderState()}
    </div>
  );
};

export default App;

"use client";
import Header from "../Components/header";
import { useState, Suspense } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

function Inputs(props) {
    return (
        <div className="md:my-10">
            <h2 className="font-light underline underline-offset-2 decoration-sky-200">
                {props.h2}
            </h2>
            <input
                required
                minLength={props.Length || 1}
                className="placeholder:text-gray-500 placeholder:italic placeholder:text-xl
            placeholder:text-center border-1 border-indigo-300
            md:border-2 m-3"
                onChange={props.onChange}
                placeholder={props.placeholder}
                type={props.type || "text"}
                value={props.value}
                disabled={props.Disabled}
            />
        </div>
    );
}

export function Register() {

    const [email, setEmail] = useState("");
    const [user, setUser] = useState("");
    const [password, setPassword] = useState("");
    const [secondPassword, setSecondPassword] = useState("");
    const [styleForm, setStyleForm] = useState("");
    const [disabled, setDisabled] = useState("");

    const router = useRouter();

    const sendInfo = async (event) => {
        event.preventDefault();
        setDisabled(true);
        setStyleForm("mt-30 md:m-10 w-fit p-10 md:p-25 rounded text-black shadow-2xl md:text-3xl select-none blur-sm");
        const data = {
            email: email,
            user: user,
            password: password,
            secondPassword: secondPassword
        };
        try {
            const request = await axios.post("http://localhost:8000/forms/process_register/", data, { validateStatus: () => true });
            if (request.status == 201) {
                console.log(request.data);
            }
        }
        catch (err) {
            console.log(err);
        }
    }

    // Unfortunately, NextJs does not support i18n yet, so we have to use a workaround.
    // That's why i'm using "decodeURIComponents" below.

    const styleDiv = "mt-30 md:m-10 w-fit p-10 md:p-25 rounded text-black shadow-2xl md:text-3xl";
    return (
        <section>
            <Header h1="M&M vendedores" />
            <form onSubmit={(event) => sendInfo(event) }>
                <section className="flex justify-center items-center box-border">
                    <div className={styleForm || styleDiv}>
                        <h1 className="md:mb-10 text-center font-sans font-light text-shadow-lg/10">Cadastro</h1>

                        <Inputs onChange={(event) => { setEmail(event.target.value); }} value={email}
                            placeholder="Digite seu Email" h2="Email" disabled={disabled} />
                        <Inputs onChange={(event) => { setUser(event.target.value); }} value={user}
                            placeholder={decodeURIComponent("Digite%20seu%20nome%20de%20usu%C3%A1rio")
                            } h2={decodeURIComponent("Usu%C3%A1rio")
                            } disabled={disabled} />
                        <Inputs onChange={(event) => { setPassword(event.target.value); }} value={password} type={"password"}
                            placeholder="Digite sua senha" h2="Senha" disabled={disabled} Length={8}
                        />

                        <Inputs onChange={(event) => { setSecondPassword(event.target.value); }} value={secondPassword} type={"password"}
                            placeholder="Digite sua senha novamente" h2="Repita sua senha" disabled={disabled} Length={8}
                        />

                    <button className="bg-indigo-600 font-light text-white rounded p-2 w-full shadow-2xl
                    hover:opacity-75 cursor-pointer transition ease-out duration-500 hover:scale-105">Cadastrar</button>
                    </div>
                </section>
            </form>
        </section>
    );
}

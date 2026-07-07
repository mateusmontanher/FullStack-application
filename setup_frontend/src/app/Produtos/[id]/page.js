"use client";
import { useEffect, useState } from "react";
import Header from "../../Components/header";
import Footer from "../../Components/footer";
import axios from "axios";
import { loadStripe } from "@stripe/stripe-js";


function ProductPage({ params }) {
    const { id: EncodedID } = params;
    const [product, setProduct] = useState(null);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);
    const [images, setImages] = useState([]);

    const [quantity, setQuantity] = useState(0);
    const [optionClothe, setOptionClothe] = useState("");

    const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);
    useEffect(() => {
        if (!EncodedID) return;

        const url = `http://localhost:8000/API/Crud/${decodeURIComponent(EncodedID)}/`;
        fetch(url)
            .then((response) => response.json())
            .then((data) => {
                setProduct(data);
                setImages([data.image, ...data.images.map((imgObj) => imgObj.image)]);
            })
            .catch((e) => {
                alert("Houve um erro durante o carregamento das informações:\n" + e.message);
            });
    }, [EncodedID]);


    const StripeCheckout = async () => {
        const url = "http://localhost:8000/Payments/create-checkout-session/";
        console.log("Esse é o valor de quantity: ",quantity);
        console.log("Esse é o valor de image: ", product.image);
        console.log("Esse é o valor de product: ", product.price);
        if (!localStorage.getItem("user")) {
            alert("User not found, you will be redirect to Login page");
            window.location.href = "/Login";
        }
        const data = {
            name: product.name,
            amount: product.price,
            ImageAdress: product.image,
            quantity: quantity,
            User: localStorage.getItem("user"),
            Option: optionClothe
        }
        console.log(data);
        try {
            console.log("Tentando fazer a requisicao para o backend");
            const request = await axios.post(url, data, { validateStatus: () => true });
            const { id: sessionId } = request.data;
            console.log("Requisicao feita com sucesso, e o id da sessao e: \n", sessionId);
            if (request.status == 200) {
                const stripe = await stripePromise;
                const { error } = await stripe.redirectToCheckout({ sessionId });
                if (error) {
                    console.error("Error:", error);
                }
            }
        } catch (e){
            console.log("Houve um erro, e o erro e: \n",e.message);
        }

    }

    if (!product) return (<p>Carregando...</p>);
    console.log(product);
    if (product.amount === 0) return alert("estoque esgotado, volte para a home page"), window.location.href = "/";

    return (
        <>
            <Header h1="M&M vendedores" />

            <section className="hidden md:block">

                <div className="flex text-2xl justify-between md:m-10 relative m-9 ">


                    <div className="flex items-center justify-center scale-90 ">
                        <button
                            onClick={() => setCurrentImageIndex((prev) => (prev > 0 ? prev - 1 : images.length - 1))}
                            className="sm:relative md:relative scale-80 md:scale-100 left-0 bg-gray-700 text-white p-2 rounded-full hover:bg-gray-900"
                        >
                            ◀
                        </button>

                        <img
                            src={images[currentImageIndex]}
                            className="rounded h-90 w-90 md:h-200 md:w-200 sm:scale-110 md:scale-100 transition duration-500 ease-in-out relative "
                            alt="Product"
                        />

                        <button
                            onClick={() => setCurrentImageIndex((prev) => (prev + 1) % images.length)}
                            className="relative md:relative scale-80 md:scale-100 right-0 bg-gray-700 text-white p-2 rounded-full hover:bg-gray-900"
                        >
                            ▶
                        </button>
                    </div>


                    <div className="flex flex-col mx-5 p-0 scale-80 md:scale-90 ">

                        <h1 className="text-6xl my-5 text-shadow-lg">{product.name}</h1>
                        <p className="text-3xl my-3 font-light ">{product.price} R$</p>

                        <div className="flex m-2 ">
                            <select className="mb-3 bg-gray-300 mx-5 w-fit rounded border-none">
                                {product.clothes_size_color_stock.map((value, index) => (
                                    <>
                                        <option key={index} onClick={(event) => { setOptionClothe(event.target.value) }}>
                                            tamanho: {value.size.name}
                                        </option>

                                        <option>
                                            cor: {value.color.name}
                                        </option>

                                        <option>
                                            unidades: {value.amount}
                                        </option>
                                    </>
                                ))}
                            </select>
                        </div>


                        <button className="bg-sky-500 text-xl rounded-full p-4 text-white text-shadow-2lg transition ease-in-out hover:bg-sky-600 hover:cursor-pointer focus:bg-sky-600 " onClick={() => {StripeCheckout()} }>Comprar</button>
                        <p className="text-gray-500 my-3 ">{product.description}</p>
                    </div>

                </div>
            </section>

            <section className="block md:hidden">
                <div className="flex flex-col ">


                    <h1 className="text-2xl text-center mt-5 text-shadow-lg">{product.name}</h1>
                    <div className="flex items-center justify-center scale-90 ">
                        <button
                            onClick={() => setCurrentImageIndex((prev) => (prev > 0 ? prev - 1 : images.length - 1))}
                            className="sm:relative md:relative scale-80 md:scale-100 left-0 bg-gray-700 text-white p-2 rounded-full hover:bg-gray-900"
                        >
                            ◀
                        </button>

                        <img
                            src={images[currentImageIndex]}
                            className="scale-110 rounded mt-8 mx-5"
                            alt="Product"
                        />

                        <button
                            onClick={() => setCurrentImageIndex((prev) => (prev + 1) % images.length)}
                            className="relative md:relative scale-80 md:scale-100 right-0 bg-gray-700 text-white p-2 rounded-full hover:bg-gray-900"
                        >
                            ▶
                        </button>
                    </div>


                    <div className="flex flex-col mx-5 p-0 scale-80 md:scale-90 ">
                        <p className="text-3xl text-center my-3 font-light ">{product.price} R$</p>

                        <div className="flex items-center justify-center m-2 ">

                            <select className="mb-3 bg-gray-300 mx-5 w-fit rounded border-none">
                                {product.clothes_size_color_stock.map((value, index) => (
                                    <option key={index} onClick={(event) => {setOptionClothe(event.target.value) } }>
                                        tamanho: {value.size.name}, cor: {value.color.name}, unidades: {value.amount}
                                    </option>
                                ))}
                            </select>

                        </div>

                        <button className="bg-sky-500 text-xl rounded-full p-4 text-white text-shadow-2lg transition ease-in-out hover:bg-sky-600 hover:cursor-pointer focus:bg-sky-600 " onClick={() => { StripeCheckout() }}>
                            Comprar
                        </button>

                        <p className="text-gray-500 my-3 ">{product.description}</p>
                    </div>


                </div>

            </section>

        </>
    );
}

export default ProductPage;

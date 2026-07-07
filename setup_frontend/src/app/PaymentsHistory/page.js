"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import Header from "../Components/header";

function Payments(){

    const [product, setProduct] = useState(null);

    useEffect(() => {
        const takeAccessToken = localStorage.getItem("access");
        const takeRefreshToken = localStorage.getItem("refresh");

        async function getProducts() {
            try {
                const requestProductsUserInfo = await fetch("http://localhost:8000/forms/process_user_payments/", {
                    method: 'GET',
                    headers: {
                        'Content-Type': "application/json", 'authorization': `Bearer ${takeAccessToken}`
                    },
                });

                if (requestProductsUserInfo.ok) {
                    const data = await requestProductsUserInfo.json();
                    setProduct(data.Products);
                }
            } catch (e) {
                console.error("Erro ao buscar o histórico de compras:", e);
            }
        }

        getProducts();

    }, [])

    if (!product) return <section className="flex flex-col justify-center items-center text-2xl my-100 line-clamp-1">
        <p>Nenhuma compra realizada...</p>
        <Link href="/">

            <p className="my-5 text-sky-400 hover:underline focus:underline">Que tal fazer a primeira?</p>

        </Link>
    </section>;

    console.log("Veja as compras realizadas pelo usuario: ", product);
    return (
        <>
            <Header h1="M&M vendedores" />
            <section>
                {product.map((products) => {
                    return (
                        <h1 key={products.Product}>Nome: {products.Product}</h1>,
                        <img key={products.Product} src={products.Image}></img>,
                        <p key={products.Product}>Valor: {products.Value}</p>,
                        <p key={products.Product}> Quantidade: {products.Amount} </p>,
                        <p key={products.Product}>Data da compra: {products.Date}</p>,
                        <p key={products.Product}>Comprada por: {products.User}</p>
                    );
                })}
            </section>
        </>
    );
}

export default Payments;

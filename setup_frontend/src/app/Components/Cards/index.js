"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

function Cards() {
    const [products, setProducts] = useState([]);
    const [filteredProducts, setFilteredProducts] = useState([]);
    const [category, setCategory] = useState("");
    const [allCategories, setAllCategories] = useState([]);
    const router = useRouter();

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                const response = await fetch("http://localhost:8000/API/Crud/");
                const data = await response.json();
                setProducts(data);
                setFilteredProducts(data);
            } catch (error) {
                console.error("Erro ao buscar produtos:", error);
            }
        };

        const fetchCategories = async () => {
            try {
                const response = await fetch("http://localhost:8000/forms/categories/");
                const data = await response.json();
                setAllCategories(data);
            } catch (error) {
                console.error("Erro ao buscar categorias:", error);
            }
        };

        fetchCategories();
        fetchProducts();
    }, []);

    const handleCategorySelect = (selectedCategory) => {
        setCategory(selectedCategory);

        if (selectedCategory === "") {
            setFilteredProducts(products);
            return;
        }

        const filtered = products.filter(product =>
            product.category.some(cat => cat.name === selectedCategory)
        );

        setFilteredProducts(filtered);
    };

    const SendInfoToDynamicPage = (ID) => {
        const encodedID = encodeURIComponent(ID);
        router.push(`/Produtos/${encodedID}`);
    };

    const categories = ["Masculino", "Feminino", "Juvenil", "Adulto", "Infantil"];

    return (
        <section className="section_cards box-border">

            <div className="flex flex-col justify-center items-center md:underline md:underline-offset-2 decoration-3 decoration-indigo-100 m-5">
                <p className="p-4 font-sans font-light text-3xl md:text-8xl">Veja o nosso
                    <span className="
                        bg-gradient-to-r
                        from-sky-700 to-indigo-800
                        bg-clip-text mx-2 md:mx-5
                        transition ease-in-out duration-900
                        hover:bg-gradient-r hover:from-indigo-800 hover:to-purple-600
                        font-sans font-light text-transparent">
                        catálogo:
                    </span>
                </p>
            </div>

            <section className="flex mb-20 md:flex-row items-start md:items-center">

                <aside className="mx-5 md:scale-100 scale-75">
                    <div className="flex flex-col gap-2">
                        <button onClick={() => handleCategorySelect("")} className="text-md cursor-pointer hover:text-blue-900 mt-2 text-blue-600 underline">
                            Limpar filtro
                        </button>
                        {categories.map((cat) => (
                            <div key={cat} onClick={() => handleCategorySelect(cat)} className={`
                                flex items-center gap-2 cursor-pointer outline w-fit p-2 rounded
                                outline-gray-500 my-1 transition-all
                                ${category === cat ? 'bg-sky-200' : ''}
                            `}>
                                <input
                                    type="checkbox"
                                    readOnly
                                    checked={category === cat}
                                    className="appearance-none w-5 h-5 rounded-full border border-gray-400 checked:bg-sky-500"
                                />
                                <p>{cat}</p>
                            </div>
                        ))}
                    </div>
                </aside>

                <section className="flex flex-wrap justify-center gap-6 sm:mx-15">
                    {filteredProducts.length === 0 ? (
                        <p>Nenhum produto encontrado para essa categoria.</p>
                    ) : (
                        filteredProducts.map((item) => (
                            <div key={item.id} className="bg-gray-100 rounded shadow-lg shadow-sky-500 p-5 w-72
                                transition duration-700 ease-in-out hover:scale-105 hover:shadow-xl cursor-pointer">
                                <img src={item.image} className="rounded w-full h-40 object-cover" alt={item.name} />
                                <h1 className="text-xl mt-4 font-medium">{item.name}</h1>
                                <p className="my-2 text-lg text-gray-700">R$ {item.price}</p>
                                <button
                                    onClick={() => SendInfoToDynamicPage(item.id)}
                                    className="text-white bg-indigo-600 px-4 py-2 mt-2 rounded hover:scale-105 transition"
                                >
                                    Comprar
                                </button>
                            </div>
                        ))
                    )}
                </section>
            </section>
        </section>
    );
}

export default Cards;

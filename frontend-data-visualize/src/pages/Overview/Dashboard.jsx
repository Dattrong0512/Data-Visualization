import React, { useEffect } from "react";

const Dashboard = () => {
    useEffect(() => {
        const divElement = document.getElementById("viz1735129772200");
        const vizElement = divElement.getElementsByTagName("object")[0];
        vizElement.style.width = "100%";
        vizElement.style.height = (divElement.offsetWidth * 0.49) + "px";

        const scriptElement = document.createElement("script");
        scriptElement.src = "https://public.tableau.com/javascripts/api/viz_v1.js";
        vizElement.parentNode.insertBefore(scriptElement, vizElement);
    }, []);

    return (
        <div
            className="tableauPlaceholder w-full h-full"
            id="viz1735129772200"
            style={{ position: "relative" }}
        >
            <noscript>
                <a href="#">
                    <img
                        alt="Sales Pipeline Cockpit"
                        src="https://public.tableau.com/static/images/CK/CK_17357925225930/Dashboard12/1_rss.png"
                        style={{ border: "none" }}
                    />
                </a>
            </noscript>
            <object
                className="tableauViz"
                style={{ display: "none" }}
            >
                <param name="host_url" value="https%3A%2F%2Fpublic.tableau.com%2F" />
                <param name="embed_code_version" value="3" />
                <param name="site_root" value="" />
                <param name="name" value="CK_17357925225930/Dashboard12" />
                <param name="tabs" value="yes" />
                <param name="toolbar" value="yes" />
                <param name="static_image" value="https://public.tableau.com/static/images/CK/CK_17357925225930/Dashboard12/1.png" />
                <param name="animate_transition" value="yes" />
                <param name="display_static_image" value="yes" />
                <param name="display_spinner" value="yes" />
                <param name="display_overlay" value="yes" />
                <param name="display_count" value="yes" />
                <param name="language" value="en-US" />
            </object>
        </div>
    );
};

export default Dashboard;
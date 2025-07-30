import streamlit as st
import subprocess
import tempfile
import os
from smartrun.envc.envc import Env

st.title("SmartRun Web Interface")
# Environment selection
env_complete = Env()
current_env = env_complete.get()
col1, col2 = st.columns(2)
with col1:
    st.write("**Current Environment:**")
    if current_env["active"]:
        st.success(f"{current_env['type']}: {current_env['name']}")
    else:
        st.warning("No virtual environment active")
# Script input
script_content = st.text_area(
    "Enter your Python script:", height=300, placeholder="print('Hello from SmartRun!')"
)
# Environment options
env_option = st.selectbox("Run in environment:", ["auto", "current", "conda", "venv"])
# Run button
if st.button("Run Script", type="primary"):
    if script_content.strip():
        with st.spinner("Running script..."):
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as f:
                    f.write(script_content)
                    script_path = f.name

                # Run script
                result = subprocess.run(
                    ["smartrun", script_path, "--env", env_option],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                # Display results
                if result.stdout:
                    st.success("Output:")
                    st.code(result.stdout, language="text")

                if result.stderr:
                    st.error("Errors:")
                    st.code(result.stderr, language="text")

                if result.returncode != 0:
                    st.error(f"Script exited with code: {result.returncode}")
                else:
                    st.success("Script completed successfully!")

            except subprocess.TimeoutExpired:
                st.error("Script execution timed out (30 seconds)")
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                # Clean up
                if "script_path" in locals():
                    os.unlink(script_path)
    else:
        st.warning("Please enter a script to run")
# File upload option
st.divider()
uploaded_file = st.file_uploader("Or upload a Python file:", type=["py"])
if uploaded_file and st.button("Run Uploaded File"):
    content = uploaded_file.read().decode()
    # Process similar to above...
